frappe.ui.form.on('Stock Entry', {
    after_save: function (frm) {
		if (frm.doc.purpose==='Material Transfer') {
			frappe.call({
				method: 'zomoamerica.api.stock_entry_calculate_total_tobacoo_weight',
				args: {
					'doc': frm.doc,
				},
				async: false,
				callback: (r) => {
					frm.reload_doc()
				},
				error: (r) => {
					// on error
				}
			})			
		}

},	
	refresh: function(frm) {
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__('Material Request:Withdrawal Request'), function () {
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
		}
	}
})