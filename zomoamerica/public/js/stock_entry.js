frappe.ui.form.on('Stock Entry', {
	refresh(frm) {
        if (frm.doc.docstatus===0) {
			frm.add_custom_button(__('Material Request : Withdrawal Request'), function() {
				erpnext.utils.map_current_doc({
					method: "zomoamerica.api.make_stock_entry",
					source_doctype: "Material Request",
					target: frm,
					date_field: "schedule_date",
					setters: {
						company: frm.doc.company,
					},
					get_query_filters: {
						docstatus: 1,
						material_request_type: ["=", ["Withdrawal Request"]],
						status: ["not in", ["Transferred", "Issued"]]
					}
				})
            }, __("Get items from"));
        }		// your code here
	}
})
