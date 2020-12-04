# -*- coding: utf-8 -*-
import json, codecs, re
from warnings import warn
import xml.etree.cElementTree as ET

PREFIXES = ["м.", "вз.", "жк.", "ул.", "бул."]
TYPOS = {"жр. Орфей": "жк. Орфей",
         "бул.Съединение": "бул. Съединение",
         "Georgi Benkovski": "ул. Георги Бенковски",
         "Macedonia": "ул. Македония",
         "ул. Дрян № 8": "ул. Дрян"}
re_cyrillic = re.compile(r'[а-яА-Я,\.\s\(\)\-0-9IVX\"]*$')

def is_cyrillic(text):
    return re_cyrillic.match(text) is not None

    
    
def audit(value, subkey):
    """ Ensure uniform address convention.
    Street prefix set to abbreviated format in Bulgarian (see src).
    Unless otherwise specified, the prefix is assumed to be "street": "ul." "ул.". 
    *src: http://www.upu.int/fileadmin/documentsFiles/activities/addressingUnit/bgrEn.pdf
    """
    if subkey == "street":
        value = value.replace("\"", "").replace("'","") #remove quotes
        value = value.replace("улица", "")
        if not is_cyrillic(value):
            if value not in TYPOS:
                warn("Non-cyrillic street name: {}. Consider manually fixing in TYPOS".format(value))
                return None
        words = value.split()
        prefix = words[0]
        if prefix in PREFIXES:
            value = prefix + " " + " ".join(words[1:]).title().replace("i","II")
        elif value in TYPOS:
            value = TYPOS[value]
        else:
            value = "ул. " + value.title().replace("i","II")
    if subkey == "postcode":
        if len(value) == 4 and value.isnumeric():
            value = int(value)
            if value < 4000 or value > 7000:
                warn("Postcode outside region of interest (4000-7000): {}".format(value))
        else:
            warn("Postcode in wrong format: {}".format(value))
            return None

    return value
    
def update(node, k, v):
    """
    Update address stacked fields to an address object
    """
    if "address" not in node:
        node["address"] = {}
    
    try:
        addr, subkey = k.split(":")
    except ValueError:
        warn("Address entry doesn't match the schema: <'{k}':'{v}'. Skipped."
                .format(k=k, v=v))
        subkey = k
    audited_value =  audit(v, subkey)
    if audited_value is not None:
        node["address"][subkey] = audited_value
    return node


def _main(filename, log_filename):
    """Iterate over XML file and execute operatons"""
    data = []
    
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            continue
        node = {}
        for kv in element.findall("tag"):
            k = kv.attrib["k"]
            v = kv.attrib["v"]
            if "addr" in k:
                node = update(node, k, v)
        if node != {}:    
            data.append(node)
    with codecs.open(log_filename, "w", encoding="utf-8") as log: 
        #https://stackoverflow.com/questions/18337407/saving-utf-8-texts-in-json-dumps-as-utf8-not-as-u-escape-sequence
        log.write(json.dumps(data, indent=2, ensure_ascii=False)+"\n")
#procedural
if __name__=="__main__":
    xml_filename = "one-tenth.osm"
    log_filename = "audit_address.json"
    _main(xml_filename, log_filename)