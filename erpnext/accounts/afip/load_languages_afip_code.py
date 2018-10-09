from load_countries_afip_code import Translate
from erpnext.accounts.afip.afip import AFIP
import frappe

def load_language_codes():
    # convert afip languages to {name, code} dictionary
    afip_languages = list(map(lambda l: {"name": l.split("|")[2], "code": l.split("|")[1]}, AFIP().get_service(AFIP.WSFEX).GetParamIdiomas()))

    for language in frappe.get_all("Language", fields=["*"]):
        language_in_spanish = Translate(language["language_code"], "es", language["language_name"])
        afip_language = get_afip_language(language_in_spanish, afip_languages)
        if afip_language:
            language_object = frappe.get_doc("Language", language["language_code"])
            language_object.afip_code = afip_language["code"]
            language_object.save()


def get_afip_language(language, afip_languages):
    if not language:
        return None
    found = filter(lambda l: l["name"].upper() in language.upper(), afip_languages)
    return found[0] if found else None

