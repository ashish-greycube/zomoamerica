// Copyright (c) 2020, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tobacco Legal Compliance", {
  refresh: function(frm) {
    let current_year = new Date().getFullYear();
    let options = [current_year, current_year - 1, current_year - 2];
    frm.set_df_property("year", "options", options);

    frm.page.add_inner_button("Download Compliance Report", () => {
      frm.trigger("download_pdf");
    });
  },

  download_pdf: function(frm, cdt, cdn) {
    var w = window.open(
      frappe.urllib.get_full_url(
        "/api/method/zomoamerica.zomoamerica.doctype.tobacco_legal_compliance.tobacco_legal_compliance.download_tlc?" +
          "docname=" +
          frm.doc.name
      )
    );
    if (!w) {
      frappe.msgprint(__("Please enable pop-ups"));
      return;
    }
  },
  fetch_opening_stock:function(frm) {
    if (frm.doc.month && frm.doc.year) {
      frappe.show_alert({message:__("Opening stock set for  {0},{1} successfully", [frm.doc.month,frm.doc.year]), indicator:'green'});
      return frm.call('set_opening_stock');
    }else{
      let message='Month & Year is required to fetch opening stock'
      frappe.show_alert({message:__(message), indicator:'red'});
    }
  }
});
