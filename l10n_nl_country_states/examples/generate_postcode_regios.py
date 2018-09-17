#!/usr/bin/python
# this script is compatible with a python3 interpreter
# this script generates the data file for postcode state mapping

import argparse
import xlrd

'''
This expected input is an .xls file, passed as argument.
The .xls file should contain the mapping of postcodes-provinces.
Note: the records of the .xls MUST be sorted by postcode number!
'''

parser = argparse.ArgumentParser()
parser.add_argument('file', type=open)
args = parser.parse_args()

workbook = xlrd.open_workbook(args.file.name)

XLS_COLUMN_CODE = 0  # xls offset for column postcode
XLS_COLUMN_PROV = 1  # xls offset for column province


def get_record_txt():
    global province
    return str('<record id="zip_%s_%s" model="res.country.state.nl.zip">\n'
               '    <field name="min_zip">%s</field>\n'
               '    <field name="max_zip">%s</field>\n'
               '    <field name="state_id" ref="state_%s" />\n'
               '</record>\n'
               ) % (
               str(last_min_zip),
               str(last_max_zip),
               str(last_min_zip),
               str(last_max_zip),
               province,
    )


for sheet in workbook.sheets():
    result_text = ''
    last_min_zip = 1000
    last_max_zip = 1000
    last_province = ''

    for row in range(1, sheet.nrows):
        code = sheet.cell_value(row, XLS_COLUMN_CODE)
        prov = sheet.cell_value(row, XLS_COLUMN_PROV).lower().replace(' ', '')
        if not code:
            pass
        elif int(code) <= last_max_zip:
            last_province = prov
            last_max_zip = int(code)
        elif int(code) == (last_max_zip + 1) and last_province == prov:
            last_max_zip = int(code)
        else:
            code = str(int(code))
            province = prov
            result_text += get_record_txt()

            last_min_zip = int(code)
            last_max_zip = int(code)
            last_province = prov

    result_text += get_record_txt()
    print(result_text)
