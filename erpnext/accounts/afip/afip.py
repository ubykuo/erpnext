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

class AFIP(object):

    _instance = None

    WSFE = "wsfe"
    WSFEX = "wsfex"

    services_classes = {"wsfe": WSFEv1, "wsfex": WSFEXv1}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AFIP, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.services = {}

    def get_service(self, service_name, company=None):
        if not self.services.get(service_name,None) or self.services.get(service_name).TicketAcessoExpirado():
            self.services[service_name] = self.connect(service_name, company)
        self.test_connection(self.services[service_name])
        return self.services[service_name]

    def connect(self, service_name, company=None):
        company = frappe.get_doc("Company", erpnext.get_default_company()) if company is None else company
        if not company or not company.cuit:
            frappe.throw(_("Company CUIT is required to connect to AFIP"))
        wsaa = WSAA()
        access_ticket = wsaa.Autenticar(service_name, CERT, PRIVATEKEY, debug=True)
        service = self.services_classes.get(service_name)()
        service.SetTicketAcceso(access_ticket)
        service.Cuit = company.cuit
        return service

    def test_connection(self, service):
        connection_ok = service.Conectar()
        if not connection_ok:
            frappe.throw(_("Error while connecting to AFIP"))

    def authorize_invoice(self, invoice):
        afip_settings = frappe.get_doc("AFIP Settings", None)
        service_name = self.WSFEX if invoice.invoice_type == afip_settings.export_invoice_code else self.WSFE
        service = self.get_service(service_name, invoice.get_company())

        try:
            exchange_rate = service.ParamGetCotizacion(invoice.get_currency().afip_code)
        except KeyError as e:
            frappe.throw(_("Invalid Currency, Check AFIP code"))

        service.add_invoice(invoice, exchange_rate, afip_settings)
        service.CAESolicitar()
        if service.Resultado == 'A':
            invoice.db_set("cae", service.CAE)
            invoice.db_set("cae_due_date", service.get_cae_due_date())
        else:
            frappe.throw(service.Obs + service.ErrMsg)
