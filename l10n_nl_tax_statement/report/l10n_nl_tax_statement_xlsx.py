# Copyright 2023 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class NLTaxStatementXlsx(models.AbstractModel):
    _name = "report.l10n_nl_tax_statement.report_tax_statement_xlsx"
    _description = "NL Tax Statement XLSX report"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objects):
        # Initialize common report variables
        report_data = {
            "workbook": workbook,
            "sheet": None,  # main sheet which will contains report
            "columns": self._get_report_columns(),  # columns of the report
            "row_pos": None,  # row_pos must be incremented at each writing lines
            "formats": None,
        }

        # One sheet per statement
        for obj in objects:
            # Initialize per-sheet variables
            report_name = obj.name
            self._define_formats(obj, workbook, report_data)
            report_data["sheet"] = workbook.add_worksheet(report_name)
            self._set_column_width(report_data)

            # Fill report
            report_data["row_pos"] = 0
            self._write_report_title(report_name, report_data)
            self._generate_report_content(obj, report_data)

    def _get_report_filters(self, report):
        return [
            [_("Date from"), report.from_date.strftime("%d/%m/%Y")],
            [_("Date to"), report.to_date.strftime("%d/%m/%Y")],
        ]

    def _set_column_width(self, report_data):
        """Set width for all defined columns.
        Columns are defined with `_get_report_columns` method.
        """
        for position, column in report_data["columns"].items():
            report_data["sheet"].set_column(position, position, column["width"])

    def _define_formats(self, obj, workbook, report_data):
        """Add cell formats to current workbook.
        Those formats can be used on all cell.
        Available formats are :
         * bold
         * header_left
         * header_right
         * row_odd
         * row_pair
         * row_amount_odd
         * row_amount_pair
        """
        color_row_odd = "#FFFFFF"
        color_row_pair = "#EEEEEE"
        color_row_header = "#FFFFCC"
        num_format = "#,##0." + "0" * obj.currency_id.decimal_places

        report_data["formats"] = {
            "bold": workbook.add_format({"bold": True}),
            "header_left": workbook.add_format(
                {
                    "bold": True,
                    "align": "left",
                    "border": False,
                    "bg_color": color_row_header,
                }
            ),
            "header_right": workbook.add_format(
                {
                    "bold": True,
                    "align": "right",
                    "border": False,
                    "bg_color": color_row_header,
                }
            ),
            "row_odd": workbook.add_format(
                {"border": False, "bg_color": color_row_odd}
            ),
            "row_pair": workbook.add_format(
                {"border": False, "bg_color": color_row_pair}
            ),
            "row_amount_odd": workbook.add_format(
                {"border": False, "bg_color": color_row_odd}
            ),
            "row_amount_pair": workbook.add_format(
                {"border": False, "bg_color": color_row_pair}
            ),
        }
        report_data["formats"]["row_amount_odd"].set_num_format(num_format)
        report_data["formats"]["row_amount_pair"].set_num_format(num_format)

    def _get_report_columns(self):
        """Define the report columns used to generate report"""
        return {
            0: {"header": _("Code"), "field": "code", "width": 5},
            1: {"header": _("Name"), "field": "name", "width": 60},
            2: {"header": _("Turnover"), "field": "omzet", "width": 14},
            3: {"header": _("VAT"), "field": "btw", "width": 14},
        }

    def _write_report_title(self, title, report_data):
        """Write report title on current line using all defined columns width.
        Columns are defined with `_get_report_columns` method.
        """
        report_data["sheet"].merge_range(
            report_data["row_pos"],
            0,
            report_data["row_pos"],
            len(report_data["columns"]) - 1,
            title,
            report_data["formats"]["bold"],
        )
        report_data["row_pos"] += 2

    def _write_filters(self, filters, report_data, sep=" "):
        """Write one line per filter, starting on current row"""
        for title, value in filters:
            report_data["sheet"].write_string(
                report_data["row_pos"],
                1,
                title + sep + value,
            )
            report_data["row_pos"] += 1
        report_data["row_pos"] += 2

    def format_line_from_obj(self, line, report_data, is_pair_line):
        """Write statement line on current row"""
        is_group = line["is_group"]
        for col_pos, column in report_data["columns"].items():
            value = line[column["field"]]

            # Write code and name
            if column["field"] in ["code", "name"]:
                report_format = (
                    report_data["formats"]["row_pair"]
                    if is_pair_line
                    else report_data["formats"]["row_odd"]
                )
                report_format = (
                    report_data["formats"]["header_left"] if is_group else report_format
                )

                report_data["sheet"].write_string(
                    report_data["row_pos"],
                    col_pos,
                    value or "",
                    report_format,
                )

            # Write amount values
            if column["field"] in ["omzet", "btw"]:
                if is_group:
                    report_data["sheet"].write_string(
                        report_data["row_pos"],
                        col_pos,
                        column["header"],
                        report_data["formats"]["header_right"],
                    )
                else:
                    to_display = (
                        column["field"] == "omzet" and line.format_omzet is not False
                    ) or (column["field"] == "btw" and line.format_btw is not False)
                    if to_display:
                        report_format = (
                            report_data["formats"]["row_amount_pair"]
                            if is_pair_line
                            else report_data["formats"]["row_amount_odd"]
                        )
                        report_data["sheet"].write_number(
                            report_data["row_pos"], col_pos, float(value), report_format
                        )
                    else:
                        report_format = (
                            report_data["formats"]["row_pair"]
                            if is_pair_line
                            else report_data["formats"]["row_odd"]
                        )
                        # Nothing to be displayed: empty cell
                        report_data["sheet"].write_string(
                            report_data["row_pos"],
                            col_pos,
                            "",
                            report_format,
                        )
        report_data["row_pos"] += 1

    def _generate_report_content(self, obj, report_data):
        """Write statement content"""
        # Write filters
        filters = self._get_report_filters(obj)
        self._write_filters(filters, report_data)

        # Case no lines found
        if not obj.line_ids:
            return

        # Write report lines
        is_pair_line = 0
        for line in obj.line_ids:
            self.format_line_from_obj(line, report_data, is_pair_line)
            is_pair_line = 1 if not is_pair_line and not line.is_group else 0
