// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('AFIP Settings', {
	refresh: function(frm) {

	},
	onload: function (frm) {
		frappe.call({
			"method": "erpnext.accounts.doctype.afip_settings.afip_settings.get_afip_values",
			"callback": function (r) {
				if (r.message) {
					frm.set_df_property("default_export_type", "options", r.message.export_types);
					frm.set_df_property("default_iva_type", "options", r.message.iva_types);
					frm.set_df_property("default_invoice_concept", "options", r.message.invoice_concepts);
				}
            }
		});
    }
});
