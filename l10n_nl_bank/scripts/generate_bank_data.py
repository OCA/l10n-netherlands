"""
This script downloads the official list of Dutch banks from an Excel file
and formats it into an Odoo XML data file (`res_bank_data.xml`).

The script fetches an XLSX file from Betaalvereniging Nederland, dynamically
finds the header row, parses the data, and generates an XML record for each
bank suitable for the `res.bank` model in Odoo.

The output file will be placed in the '../data/' directory relative to this
script's location.
"""

import io
import logging
import os
import re
from datetime import datetime
from xml.dom import minidom
from xml.etree import ElementTree as ET

import openpyxl
import requests

# The official source for the Dutch bank registry XLSX file.
DATA_URL = "https://www.betaalvereniging.nl/wp-content/uploads/BIC-lijst-NL.xlsx"

# Define the output file path relative to the script's location.
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "..", "data", "res_bank_data.xml")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def to_custom_title_case(text):
    """
    Converts a string to title case, while keeping specific abbreviations
    like 'N.V.', 'B.V.', and 'NV' in full caps.
    """
    title_cased = text.title()
    fix_map = {
        "Nv": "NV",
        "Bv": "BV",
        "Ing": "ING",
        "Asn": "ASN",
        "Abn": "ABN",
        "Blg": "BLG",
        "Bnp": "BNP",
        "Nibc": "NIBC",
        "Xe": "XE",
        "Bunq": "BUNQ",
        "Hsbc": "HSBC",
        "Kbc": "KBC",
        "Keb": "KEB",
        "Mufg": "MUFG",
        "N.v.": "N.V.",
        "B.v.": "B.V.",
        "&amp;": "&",
    }

    words = title_cased.split()
    corrected_words = [fix_map.get(word, word) for word in words]
    return " ".join(corrected_words)


def fetch_and_process_data():
    """
    Fetches the bank data from the Excel file, finds the header row and update
    date dynamically, and processes the data.
    """
    logging.info("📥 Fetching and processing bank data from %s...", DATA_URL)

    try:
        response = requests.get(DATA_URL, timeout=10)
        response.raise_for_status()  # Check for HTTP errors
        excel_file = io.BytesIO(response.content)
        workbook = openpyxl.load_workbook(excel_file, data_only=True, read_only=True)
        worksheet = workbook.active
    except requests.exceptions.RequestException as e:
        logging.exception("❌ Error downloading the file: %s", e)
        return [], None
    except Exception as e:
        logging.exception("❌ Error reading the Excel file with openpyxl: %s", e)
        return [], None

    header_row_index = -1
    bic_col_name = "BIC"
    name_col_name = "Naam betaaldienstverlener"
    last_update_date = None

    # Step 2: Search for the header row and the update date within the first 15 rows.
    for i, row in enumerate(worksheet.iter_rows(min_row=1, max_row=15), 1):
        row_values = [str(cell.value).strip() if cell.value else "" for cell in row]

        # Check for the header row
        if (
            header_row_index == -1
            and bic_col_name in row_values
            and name_col_name in row_values
        ):
            header_row_index = i
            logging.info("✅ Found headers on row %s.", header_row_index)

        # Check for the last update date
        for cell_value in row_values:
            match = re.search(r"Laatste update:\s*(.*)", cell_value, re.IGNORECASE)
            if match:
                last_update_date = match.group(1).strip()
                logging.info("✅ Found last update date: %s", last_update_date)
                break

        # If both are found, we can stop iterating
        if header_row_index != -1 and last_update_date:
            break

    if header_row_index == -1:
        logging.error(
            "❌ Error: Could not find the header row containing '%s' and '%s'.",
            bic_col_name,
            name_col_name,
        )
        return [], None

    logging.info(
        "✅ Proceeding with data extraction from header row %s.",
        header_row_index,
    )

    processed_banks = []
    used_ids = set()

    # Get the correct column indices from the header row
    header_row = [cell.value for cell in worksheet[header_row_index]]
    try:
        bic_col_index = header_row.index(bic_col_name)
        name_col_index = header_row.index(name_col_name)
    except ValueError:
        logging.error("❌ Error: Could not find required columns in the header.")
        return [], last_update_date

    # Iterate through data rows, starting after the header
    for row in worksheet.iter_rows(min_row=header_row_index + 1):
        bic_cell = row[bic_col_index]
        name_cell = row[name_col_index]

        bic = str(bic_cell.value).strip() if bic_cell and bic_cell.value else None
        name_raw = (
            str(name_cell.value).strip() if name_cell and name_cell.value else None
        )

        if not bic or not name_raw or bic == "nan" or name_raw == "nan":
            continue

        name = to_custom_title_case(name_raw)
        base_id = bic[:4].upper().replace("_", "")
        record_id = base_id

        counter = 2
        while record_id in used_ids:
            record_id = f"{base_id}_{counter}"
            counter += 1

        used_ids.add(record_id)
        processed_banks.append((record_id, name, bic))

    logging.info("✅ Data processed successfully.")
    return sorted(processed_banks, key=lambda x: x[0]), last_update_date


def generate_xml_file(bank_data, last_update_date):
    """
    Generates the Odoo XML file from the processed bank data.
    """
    logging.info("⚙️  Generating XML file...")

    odoo_node = ET.Element("odoo")
    odoo_node.set("noupdate", "1")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

    # Add a comment for when the script was run
    comment_script = ET.Comment(f" File generated by script on {timestamp} ")
    odoo_node.append(comment_script)

    # Add a comment for the last update date from the source file
    if last_update_date:
        comment_data_date = ET.Comment(
            f" Source data last updated on: {last_update_date} "
        )
        odoo_node.append(comment_data_date)

    # Iterate through and create record elements directly under the odoo node
    for record_id, name, bic in bank_data:
        record_node = ET.SubElement(odoo_node, "record", id=record_id, model="res.bank")
        ET.SubElement(record_node, "field", name="name").text = name
        ET.SubElement(record_node, "field", name="bic").text = bic
        ET.SubElement(record_node, "field", name="country", ref="base.nl")

    # Use minidom for pretty-printing the XML
    xml_string = minidom.parseString(ET.tostring(odoo_node)).toprettyxml(
        indent="    ", encoding="utf-8"
    )

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "wb") as f:
        f.write(xml_string)

    logging.info("🎉 Success! File saved to: %s", OUTPUT_PATH)


def main():
    """Main execution function."""
    try:
        banks_list, last_update_date = fetch_and_process_data()
        if banks_list:
            generate_xml_file(banks_list, last_update_date)
    except Exception:
        # logging.exception will print the full traceback
        logging.error("An unexpected error occurred during the script execution.")


if __name__ == "__main__":
    main()
