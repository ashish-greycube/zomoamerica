from __future__ import unicode_literals
from frappe import _
import frappe


def get_data():
	config = [
		{
			"label": _("Reports"),
			"items": [
				{
					"type": "report",
					"name": "Tobacco Product Tax",
					"is_query_report": True,
					"doctype": "File"
				},
				{
					"type": "report",
					"name": "Item wise Master Case Sales",
					"is_query_report": True,
					"doctype": "File"
				},
				{
					"type":"report",
					"name":"Tobacco In Out",
					"is_query_report":True,
					"doctype": "File"
				}
			]
		},
		{
			"label": _("Setup"),
			"items": [
				{
					"type": "doctype",
					"name": "US State wise Tobacco Excise",
					"description": "US State wise Tobacco Excise"
				}
			]
		}
		]
	return config
	
