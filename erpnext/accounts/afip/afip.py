import frappe
import datetime
import os
from erpnext.accounts.afip.wsaa import WSAA
from erpnext.accounts.afip.wsfev1 import WSFEv1

CERT = os.path.dirname(os.path.abspath(__file__)) + "/ubykuoERP.crt"  # El certificado X.509 obtenido de Seg. Inf.
PRIVATEKEY = os.path.dirname(os.path.abspath(__file__)) + "/ClavePrivadaUbykuo.key"  # La clave privada del certificado CERT
CACERT = os.path.dirname(os.path.abspath(__file__)) + "/conf/afip_ca_info.crt"
CUIT = "20119613524"

def connect_afip(invoice_type):
    wsaa = WSAA()
    if invoice_type.code in (11, 1, 6):
        service_name = "wsfe"
    else:
        service_name = "wsfex"

    access_ticket = wsaa.Autenticar(service_name, CERT, PRIVATEKEY, debug=True)
    service = WSFEv1()
    connection_ok = service.Conectar()
    if not connection_ok:
        frappe.throw(_("Error while connecting to AFIP"))
    service.SetTicketAcceso(access_ticket)
    service.Cuit = CUIT
    return service

def authorize_invoice(invoice):
    authorize_local_invoice(invoice) if invoice.get_invoice_type().code in (11, 1, 6) else authorize_export_invoice(invoice)

def authorize_local_invoice (invoice):
    service = connect_afip(invoice.get_invoice_type())

    invoice_date = "".join(invoice.posting_date.split("-"))

    last_voucher_number = long (service.CompUltimoAutorizado(invoice.get_invoice_type().code, invoice.point_of_sale) or 0)

    if invoice.get_currency().currency_name == 'ARS':
        exchange_rate = '1.00'
    else:
        exchange_rate = frappe.get_value("Currency Exchange", {"date": invoice.posting_date, "to_currency": "ARS"})
        if exchange_rate:
            exchange_rate = str(exchange_rate.exchange_rate)
        else:
            frappe.throw(_("Specify Exchange Rate to convert from {0} to {1}").format(invoice.currency, "ARS"))

    service.CrearFactura(invoice.get_concept().code, invoice.get_customer().get_id_type().code, invoice.get_customer().id_number,
                      invoice.get_invoice_type().code, invoice.point_of_sale, last_voucher_number + 1, last_voucher_number + 1,
                      invoice.grand_total, 0 , invoice.grand_total,
                      0, 0, 0, invoice_date, None,
                      None, None,
                      invoice.get_currency().afip_code, exchange_rate)

    service.CAESolicitar()
    if service.Resultado == 'A':
        invoice.cae = service.CAE
        invoice.cae_due_date = datetime.datetime.strptime(service.Vencimiento, '%Y%m%d').date()
    else:
        frappe.throw(service.Obs)

def authorize_export_invoice(invoice):
    pass

