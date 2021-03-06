# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "zomoamerica"
app_title = "ZomoAmerica"
app_publisher = "GreyCube Technologies"
app_description = "Customization for Zomo America"
app_icon = "octicon octicon-flame"
app_color = "yellow"
app_email = "admin@greycube.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/zomoamerica/css/zomoamerica.css"
# app_include_js = "/assets/zomoamerica/js/zomoamerica.js"

# include js, css files in header of web template
# web_include_css = "/assets/zomoamerica/css/zomoamerica.css"
# web_include_js = "/assets/zomoamerica/js/zomoamerica.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Stock Entry": "public/js/stock_entry.js",
    "Sales Order": "public/js/sales_order.js",
    "Material Request": "public/js/material_request.js",
    "Sales Invoice": "public/js/item_uom_reset.js",
    "Delivery Note": "public/js/delivery_note.js",
    "Purchase Order": "public/js/item_uom_reset.js",
    "Purchase Invoice": "public/js/item_uom_reset.js",
    "Tobacco Legal Compliance": "public/js/tobacco.js"    
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "zomoamerica.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "zomoamerica.install.before_install"
# after_install = "zomoamerica.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "zomoamerica.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Invoice": {
        "validate": "zomoamerica.api.zomo_sales_invoice_validate"
    },
    "Sales Order": {
        "validate": "zomoamerica.api.calculate_total_tobacco_weight"
    },
    "Delivery Note": {
        "validate": "zomoamerica.api.calculate_total_tobacco_weight",
        "on_change": "zomoamerica.api.update_delivery_note_workflow_state",
        "before_cancel": "zomoamerica.api.delink_connected_stock_entry",
        "on_trash": "zomoamerica.api.delink_connected_stock_entry"
    }
    # ,
    # "Material Request": {
    #     "validate": "zomoamerica.api.set_title_for_material_request"
    # },    
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"zomoamerica.tasks.all"
# 	],
# 	"daily": [
# 		"zomoamerica.tasks.daily"
# 	],
# 	"hourly": [
# 		"zomoamerica.tasks.hourly"
# 	],
# 	"weekly": [
# 		"zomoamerica.tasks.weekly"
# 	]
# 	"monthly": [
# 		"zomoamerica.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "zomoamerica.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "zomoamerica.event.get_events"
# }
