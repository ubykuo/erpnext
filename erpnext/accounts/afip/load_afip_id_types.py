from erpnext.accounts.afip.afip import AFIP
import frappe

def load_afip_id_types():
    id_types = AFIP().get_service(AFIP.WSFE).ParamGetTiposDoc()
    id_types += AFIP().get_service(AFIP.WSFEX).GetParamDstCUIT()
    for id_type in id_types:
        id_type = id_type.split("|")
        frappe.get_doc({"doctype": "Identification Type", "code": id_type[0], "id_name": id_type[1]}).save()