#!/usr/bin/python
# this script generates the data file for postcode state mapping
# TODO: this could be much more efficient if we actually used min/max
import argparse
import xlrd

parser = argparse.ArgumentParser()
parser.add_argument('file', type=file)
args = parser.parse_args()

workbook = xlrd.open_workbook(file_contents=args.file.read())
for sheet in workbook.sheets():
    for row in range(1, sheet.nrows):
        print (
            '<record id="zip_%d" model="res.country.state.nl.zip">\n'
            '    <field name="min_zip">%d</field>\n'
            '    <field name="max_zip">%d</field>\n'
            '    <field name="state_id" ref="state_%s" />\n'
            '</record>'
        ) % (
            int(sheet.cell_value(row, 0)),
            int(sheet.cell_value(row, 0)),
            int(sheet.cell_value(row, 0)),
            sheet.cell_value(row, 5).lower().replace('-', ''),
        )
