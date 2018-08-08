import frappe
import datetime
import os
from frappe import _
from erpnext.accounts.afip.wsaa import WSAA
from erpnext.accounts.afip.wsfev1 import WSFEv1

CERT = os.path.dirname(os.path.abspath(__file__)) + "/ubykuoERP.crt"  # El certificado X.509 obtenido de Seg. Inf.
PRIVATEKEY = os.path.dirname(os.path.abspath(__file__)) + "/ClavePrivadaUbykuo.key"  # La clave privada del certificado CERT
CACERT = os.path.dirname(os.path.abspath(__file__)) + "/conf/afip_ca_info.crt"
CUIT = "20119613524"

def connect_afip(service_name):
    wsaa = WSAA()

    access_ticket = wsaa.Autenticar(service_name, CERT, PRIVATEKEY, debug=True)
    service = WSFEv1()
    connection_ok = service.Conectar()
    if not connection_ok:
        frappe.throw(_("Error while connecting to AFIP"))
    service.SetTicketAcceso(access_ticket)
    service.Cuit = CUIT
    return service

def authorize_invoice(invoice):
    authorize_local_invoice(invoice) if invoice.invoice_type in ("11", "1", "6") else authorize_export_invoice(invoice)

def authorize_local_invoice (invoice):
    service = connect_afip("wsfe")

    invoice_date = "".join(invoice.posting_date.split("-"))

    last_voucher_number = long (service.CompUltimoAutorizado(invoice.invoice_type, invoice.point_of_sale) or 0)

    if invoice.get_currency().currency_name == 'ARS':
        exchange_rate = '1.00'
    else:
        try:
            exchange_rate = service.ParamGetCotizacion(invoice.get_currency().afip_code)
        except KeyError as e:
            frappe.throw(_("Invalid Currency, Check AFIP code"))

    service.CrearFactura(invoice.concept, invoice.get_customer().get_id_type().code, invoice.get_customer().id_number,
                      invoice.invoice_type, invoice.point_of_sale, last_voucher_number + 1, last_voucher_number + 1,
                      invoice.grand_total, 0 , invoice.total,
                      0, 0, 0, invoice_date, None,
                      None, None,
                      invoice.get_currency().afip_code, exchange_rate)

    if invoice.invoice_type == "1": # Factura A
        iva_amount = (invoice.total * get_iva_rate(service,invoice.iva_type)) / 100
        service.AgregarIva(invoice.iva_type, invoice.total, iva_amount)
        service.EstablecerCampoFactura("imp_iva", iva_amount)
        service.EstablecerCampoFactura("imp_total", invoice.total + iva_amount)

    service.CAESolicitar()
    if service.Resultado == 'A':
        invoice.cae = service.CAE
        invoice.cae_due_date = datetime.datetime.strptime(service.Vencimiento, '%Y%m%d').date()
    else:
        frappe.throw(service.Obs)

def get_iva_rate(service, iva_code):
    all_iva_types = service.ParamGetTiposIva()
    selected_iva = filter(lambda i: i.split("|")[0] == iva_code , all_iva_types)
    if not selected_iva:
        frappe.throw(_("Invalid IVA Type"))
    selected_iva = selected_iva[0].split("|")
    return float(selected_iva[1][:-1]) # remove % character

def authorize_export_invoice(invoice):
    pass

