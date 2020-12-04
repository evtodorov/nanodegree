import json, codecs, re
from warnings import warn
import xml.etree.cElementTree as ET

from audit_address import is_cyrillic


    
    
def audit(value, subkey):
    """Check if local name is Cyrillic"""
    if subkey == "local":
        if not is_cyrillic(value):
            warn("Local name is not Cyrillic {}".format(value))
    value = value.replace(u"“","\"").replace(u"„","\"")
    return value
    
def update(node, k, v):
    """Update all entities to local name and English names only"""
    
    if "name" not in node:
        node["name"] = {}
    if k == "name":
        new_value = audit(v, "local")
        try:
            node["name"]["local"] = new_value
        except TypeError:
            print(node)
    elif k=="int_name" or k=="name:uk" or k=="name:en":
        node["name"]["English"] = v

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