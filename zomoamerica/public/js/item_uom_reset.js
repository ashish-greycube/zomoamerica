frappe.ui.form.on(this.frm.doctype + " Item", {
	item_code: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if(row.item_code) {
            row.uom='';
            refresh_field("uom", cdn, "items");
        }
    
    }
});