# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_iva_types, get_export_types, get_invoice_concepts

class AFIPSettings(Document):
	pass


@frappe.whitelist()
def get_afip_values():
	return {"export_types": get_export_types(), "iva_types": get_iva_types(), "invoice_concepts": get_invoice_concepts()}