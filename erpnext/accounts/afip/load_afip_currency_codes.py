import frappe


currency_map = {"ARS": "PES", "USD": "DOL"}

def load_afip_currency_codes():
    for erpnext_id, afip_id in currency_map.items():
        currency = frappe.get_doc("Currency", erpnext_id)
        if currency:
            currency.afip_code = afip_id
            currency.save()



