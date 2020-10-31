frappe.ui.form.on("Material Request",{
    validate: function(frm){
        if (frm.doc.material_request_type =='Withdrawal Request') {
            let total_qty_cf=0;
            let total_amount_cf=0;
            frappe.defaults.get_default("currency")
            let mastercase_rate_cf = frm.doc.mastercase_rate_cf
            frm.doc.items.forEach(item=> {
                total_qty_cf+=item.qty
            })
            total_amount_cf = total_qty_cf * mastercase_rate_cf
            frm.set_value("total_qty_cf",total_qty_cf);
            frm.set_value("net_weight_cf",total_qty_cf*6);
            frm.set_value("gross_weight_cf",total_qty_cf*6*1.225); 
            frm.set_value("total_amount_cf",total_amount_cf);           
        }

    }
})