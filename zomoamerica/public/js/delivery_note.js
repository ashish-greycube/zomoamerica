frappe.ui.form.on("Delivery Note", {
	refresh: function(frm) {
        if (frm.is_new()=== undefined && frm.doc.docstatus < 1 ){
        frm.add_custom_button(__('Repack'), function() {
            frappe.call({
                method: "zomoamerica.api.create_stock_entry",
                args: {
                    "source_name": frm.doc.name
                },
                freeze: true,
                callback: function (r) {
                    if (!r.exe && r.message==="There are no eligibile items for making stock entry.") {
                        frappe.msgprint(__(r.message))
                    }
                    else if(!r.exe){
                        var doc = frappe.model.sync(r.message);
                        frappe.set_route("Form", r.message.doctype, r.message.name);
                    }
                    else {
                        frappe.msgprint(__("Something went wrong.."))
                    }                    
                }
            });
        }, __('Create'));
    }
    }
});


frappe.ui.form.on(this.frm.doctype + " Item", {
	item_code: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if(row.item_code) {
            row.uom='';
            refresh_field("uom", cdn, "items");
        }
    
    }
});