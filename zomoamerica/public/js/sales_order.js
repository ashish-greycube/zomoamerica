frappe.ui.form.on('Sales Order', {
	scan_barcode(frm, e) {
		$(window).on('keydown', function (e) {
			var key = frappe.ui.keys.get_key(e);
			if (key == 'enter') {
				cur_frm.refresh_field('items')
			}
		});
	}
})

frappe.ui.form.on('Sales Order Item', {
	item_code(frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		frappe.db.get_value('Item', row.item_code, 'stock_uom')
			.then(r => {
				if (r.message.stock_uom) {
					let stock_uom = r.message.stock_uom
					row.stock_uom = stock_uom
					cur_frm.add_child("items");
				}
			})
	}
})