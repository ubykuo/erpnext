import frappe
import datetime
import os
from erpnext.accounts.afip.wsaa import WSAA
from erpnext.accounts.afip.wsfev1 import WSFEv1


WSAA_WSDL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"  # El WSDL correspondiente al WSAA
WSFE_WSDL_HOMO = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
CERT = os.path.dirname(os.path.abspath(__file__)) + "/ubykuoERP.crt"  # El certificado X.509 obtenido de Seg. Inf.
PRIVATEKEY = os.path.dirname(os.path.abspath(__file__)) + "/ClavePrivadaUbykuo.key"  # La clave privada del certificado CERT
WSAAURL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"
CACERT = os.path.dirname(os.path.abspath(__file__)) + "/conf/afip_ca_info.crt"
CUIT = "20119613524"

def connect_afip(invoice_type):
    wsaa = WSAA()
    if invoice_type.code in (11, 1, 6):
        service_name = "wsfe"
    else:
        service_name = "Exportacion"

    print service_name
    access_ticket = wsaa.Autenticar(service_name, CERT, PRIVATEKEY, debug=True)
    service = WSFEv1()
    connection_ok = service.Conectar(None, WSFE_WSDL_HOMO, "", None, True)
    if not connection_ok:
        frappe.throw(_("Error while connecting to AFIP"))
    service.SetTicketAcceso(access_ticket)
    service.Cuit = CUIT
    return service

def authorize_invoice (invoice):
    service = connect_afip(invoice.get_invoice_type())


    print (invoice.posting_date)
    invoice_date = "".join(invoice.posting_date.split("-"))

    last_voucher_number = long (service.CompUltimoAutorizado(invoice.get_invoice_type().code, invoice.point_of_sale) or 0)

    service.CrearFactura(invoice.get_concept().code, invoice.get_customer().get_id_type().code, invoice.get_customer().id_number,
                      invoice.get_invoice_type().code, invoice.point_of_sale, last_voucher_number + 1, last_voucher_number + 1,
                      invoice.grand_total, 0 , invoice.grand_total,
                      0, 0, 0, invoice_date, None,
                      None, None,
                      invoice.get_currency().afip_code, '1.00')

    service.CAESolicitar()
    if service.Resultado == 'A':
        invoice.cae = service.CAE
        invoice.cae_due_date = datetime.datetime.strptime(service.Vencimiento, '%d%m%Y').date()
    else:
        frappe.throw(service.Obs)
