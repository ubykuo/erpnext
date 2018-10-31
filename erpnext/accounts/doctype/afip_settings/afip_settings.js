// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('AFIP Settings', {
	refresh: function(frm) {

	},
	onload: function (frm) {
		frappe.call({
			"method": "erpnext.accounts.doctype.sales_invoice.sales_invoice.get_export_types",
			"callback": function (r) {
				if (r.message) {
					frm.set_df_property("default_export_type", "options", r.message);
				}
            }
		});
    }
});
