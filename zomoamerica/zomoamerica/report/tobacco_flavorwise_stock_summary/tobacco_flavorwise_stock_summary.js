frappe.query_reports["Tobacco Flavorwise Stock Summary"] = {
	"filters": [
		
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"default": frappe.sys_defaults.default_warehouse,
			"width": "120",
			"reqd":1
		}
	]
}