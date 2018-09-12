
import requests
import frappe
from erpnext.accounts.afip.afip import connect_afip

def Translate(source, target, text):
    parametros = {'sl': source, 'tl': target, 'q': text}
    cabeceras = {"Charset":"UTF-8","User-Agent":"AndroidTranslate/5.3.0.RC02.130475354-53000263 5.1 phone TRANSLATE_OPM5_TEST_1"}
    url = "https://translate.google.com/translate_a/single?client=at&dt=t&dt=ld&dt=qca&dt=rm&dt=bd&dj=1&hl=es-ES&ie=UTF-8&oe=UTF-8&inputm=2&otf=2&iid=1dd3b944-fa62-4b55-b330-74909a99969e"
    response = requests.post(url, data=parametros, headers=cabeceras)
    if response.status_code == 200:
        for x in response.json()['sentences']:
            return x['trans']
    else:
        return "Ocurrio un error"


def update_countries():
    service = connect_afip("wsfex")
    countries = service.GetParamDstPais()

    for country in countries:
        country = country.split("|")
        country_translated = Translate("es", "en", country[2])

        try:
            country_object = frappe.get_doc("Country", country_translated)
            country_object.afip_code = country[1]
            country_object.save()
        except Exception:
            # country was not found
            pass







