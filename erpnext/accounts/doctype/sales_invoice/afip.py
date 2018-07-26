import frappe
import datetime
from erpnext.afip.wsaa import WSAA
from erpnext.afip.wsfev1 import WSFEv1


WSAA_WSDL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"  # El WSDL correspondiente al WSAA
WSFE_WSDL_HOMO = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
CERT = "ubykuoERP.crt"  # El certificado X.509 obtenido de Seg. Inf.
PRIVATEKEY = "ClavePrivadaUbykuo.key"  # La clave privada del certificado CERT
WSAAURL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"
CACERT = "conf/afip_ca_info.crt"
CUIT = "20119613524"


def connect_afip(invoice_type):
    wsaa = WSAA()
    if invoice_type in ('A', 'B', 'C'):
        service_name = "wsfe"
    else:
        service_name = "Exportacion"
    access_ticket = wsaa.Autenticar(service_name, CERT, PRIVATEKEY, WSAAURL, None, None, CACERT)
    service = WSFEv1()
    connection_ok = service.Conectar(None, WSFE_WSDL_HOMO, "", None, True)
    if not connection_ok:
        frappe.throw(_("Error while connecting to AFIP"))
    service.SetTicketAcceso(access_ticket)
    service.Cuit = CUIT

def authorize_invoice (invoice):
    service = connect_afip(invoice.invoice_type)

    invoice_date = invoice.posting_date.strftime("%Y%m%d")
    last_voucher_number = nro_comprobante = long (service.CompUltimoAutorizado(invoice.invoice_type, invoice.point_of_sale) or 0)

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
