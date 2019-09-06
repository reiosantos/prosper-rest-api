import csv
import datetime

import xlrd
from django.utils.http import urlencode

from prosper_investments.apps.venue.models import VenueSetting
from prosper_investments.apps.venue.models import VenueSettingValue


def _add_venue_url_component(url, venue_url_component):
	"""URL with ?venue= query parameter"""
	return '%s?%s' % (url, urlencode({'venue': venue_url_component}))


def add_venue_to_url(url, venue):
	"""URL with ?venue= query parameter"""
	return _add_venue_url_component(url, venue.url_component)


excel_content_types = [
	'application/vnd.ms-excel',
	'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
	'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
	'application/vnd.ms-excel.sheet.macroEnabled.12',
	'application/vnd.ms-excel.template.macroEnabled.12',
	'application/vnd.ms-excel.addin.macroEnabled.12',
	'application/vnd.ms-excel.sheet.binary.macroEnabled.12'
]


# noinspection PyBroadException
def is_file_excel_document(filename):
	try:
		xlrd.open_workbook(filename)
		return True
	except:
		return False


def csv_from_excel(excel_file):
	"""
	:type excel_file: Converted file to csv format
	"""
	wb = xlrd.open_workbook(excel_file)
	sh = wb.sheet_by_index(0)
	csv_file = open('tmp_csv_file.csv', 'wb')
	wr = csv.writer(csv_file)

	for rownum in range(sh.nrows):
		if rownum == 0:
			header_row = []
			for colnum in range(sh.ncols):
				if sh.cell_type(rownum, colnum) == xlrd.XL_CELL_DATE:
					cell = xlrd.xldate.xldate_as_datetime(
						sh.cell_value(rownum, colnum), wb.datemode)
					cell = cell.replace(year=1900)
					header_row.append(datetime.datetime.strftime(cell, "%H:%M"))
				else:
					header_row.append(sh.cell_value(rownum, colnum))
			wr.writerow(header_row)
		else:
			body_row = []
			for colnum in range(sh.ncols):
				if sh.cell_type(rownum, colnum) == xlrd.XL_CELL_TEXT:
					body_row.append(sh.cell_value(rownum, colnum).encode('utf-8'))
				elif sh.cell_type(rownum, colnum) == xlrd.XL_CELL_NUMBER:
					body_row.append(int(sh.cell_value(rownum, colnum)))
				else:
					body_row.append(sh.cell_value(rownum, colnum))

			wr.writerow(body_row)

	csv_file.close()
	return csv_file


def check_venue_settings(venue, venue_settings_string):
	try:
		setting = VenueSetting.objects.get(var_define=venue_settings_string)
		VenueSettingValue.objects.get(setting=setting, venue=venue)
		return True
	except VenueSettingValue.DoesNotExist:
		return False
