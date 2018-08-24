import frappe
import erpnext
import datetime
import os
from frappe import _
from erpnext.accounts.afip.wsaa import WSAA
from erpnext.accounts.afip.wsfev1 import WSFEv1
from erpnext.accounts.afip.wsfexv1 import WSFEXv1

CERT = os.path.dirname(os.path.abspath(__file__)) + "/ubykuoERP.crt"  # El certificado X.509 obtenido de Seg. Inf.
PRIVATEKEY = os.path.dirname(os.path.abspath(__file__)) + "/ClavePrivadaUbykuo.key"  # La clave privada del certificado CERT
CACERT = os.path.dirname(os.path.abspath(__file__)) + "/conf/afip_ca_info.crt"

def get_service(service_name):
    return WSFEv1() if service_name == "wsfe" else WSFEXv1()

def connect_afip(service_name, company=None):
    company = frappe.get_doc("Company", erpnext.get_default_company()) if company is None else company
    if not company or not company.cuit:
        frappe.throw(_("Company CUIT is required to connect to AFIP"))
    wsaa = WSAA()
    access_ticket = wsaa.Autenticar(service_name, CERT, PRIVATEKEY, debug=True)
    service = get_service(service_name)
    connection_ok = service.Conectar()
    if not connection_ok:
        frappe.throw(_("Error while connecting to AFIP"))
    service.SetTicketAcceso(access_ticket)
    service.Cuit = company.cuit
    return service


def authorize_invoice (invoice):
    service_name = "wsfex" if invoice.invoice_type == "19" else "wsfe"
    service = connect_afip(service_name, invoice.get_company())

    try:
        exchange_rate = service.ParamGetCotizacion(invoice.get_currency().afip_code)
    except KeyError as e:
        frappe.throw(_("Invalid Currency, Check AFIP code"))

    service.add_invoice(invoice, exchange_rate)
    service.CAESolicitar()
    if service.Resultado == 'A':
        invoice.db_set("cae", service.CAE)
        invoice.db_set("cae_due_date", datetime.datetime.strptime(service.Vencimiento, '%Y%m%d').date())
    else:
        frappe.throw(service.Obs)






