from erpnext.accounts.afip.afip import connect_afip
import frappe

def load_afip_id_types():
    id_types = connect_afip("wsfe").ParamGetTiposDoc()
    id_types += connect_afip("wsfex").GetParamDstCUIT()
    for id_type in id_types:
        id_type = id_type.split("|")
        frappe.get_doc({"doctype": "Identification Type", "code": id_type[0], "id_name": id_type[1]}).save()