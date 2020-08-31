frappe.ui.form.on("Delivery Note", {
    after_save: function(frm) {
        if (frm.doc.customer) {
            frappe.db.get_value('Customer', frm.doc.customer, 'customer_delivery_instruction_cf')
            .then(r => {
                if (r.message.customer_delivery_instruction_cf) {
                    frappe.msgprint({
                        title: __('Customer Delivery Instruction.'),
                        indicator: 'green',
                        message: __('{0}',[r.message.customer_delivery_instruction_cf])
                    });
                }
            })         
        }
    },
    shift_unavailable_items_cf: function(frm) {
        frm.refresh_field("items");
        let items=frm.doc.items;
        for (let index = 0; index < items.length; index++) {
            const item = items[index];
            if (item.actual_qty < item.qty) {
                let shift_qty =flt(item.qty-item.actual_qty)
                item.qty=item.actual_qty
                var shift_item=frm.add_child("items_not_shipped_and_invoiced")
                shift_item.item_code=item.item_code
                shift_item.qty=shift_qty
                shift_item.uom=item.uom                
            }
            
        }
        // frm.refresh_field("items");
        // frm.refresh_field("items_not_shipped_and_invoiced");
        frm.save();
    },
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