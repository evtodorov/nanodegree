# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict
import re
import json
import codecs
from warnings import warn



import audit_address, audit_name

# based on Lesson exercises
# extended support for capital letters, numbers, minus sign & multiple colons in keys
alphanum = re.compile(r'^([a-zA-Z0-9\-]|_)*$')
alphanum_colon = re.compile(r'^([a-zA-Z0-9\-]|_)*(:([a-zA-Z0-9\-]|_)*)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

SPECIAL_FUNCTIONS = {   "addr": audit_address,
                        "name": audit_name,
                        "int_name": audit_name,
                        "wikipedia": None}
SPECIAL_PARENT_DESCRIPTIONS = { "is_in": "combined",
                                "building": "type",
                                "source": "name",
                                "railway": "type",
                                "destination": "name",
                                "brand": "name",
                                "traffic_signals": "type",
                                "capacity": "capacity",
                                "internet_access": "type",
                                "sidewalk": "side"}

def count_key_type(element, keys):
    """Helper to count key types.
    Count stacked vs non-stacked keys;
    Store unique problematic keys"""
    if element.tag == "tag":
        key =  element.attrib["k"]
        type = key_type(key)
        
        if type in ("alphanum", "alphanum_colon"):
            keys[type][key] += 1
        else:
            keys[type].add(key)

    return keys

def key_type(key):
    """Helper to define key types"""
    if alphanum.match(key) is not None:
        type = "alphanum"
    elif alphanum_colon.match(key) is not None:
        type = "alphanum_colon"
    elif len(problemchars.findall(key)) > 0:
        type = "problemchars"
    else:
        type = "other"
    return type

def get_user(element):
    """Helper to return userid"""
    return int(element.attrib["uid"])
   
def sort_dict_by_value(d):
    """
    Return Dictionary sorted by value (Python 3.6+)
    """
    #https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    return {k: v for k, v in sorted(d.items(), key=lambda item: item[1])} 
    
def find_fields_of_interest(d, thres=0.01):
    """
    Return dict of fields & count of occurences if field occurs more
    often than a certain percent (default 1%) of all fields"""
    min_v = sum(d.values()) * 0.01
    return {k: v for k, v in d.items() if v > min_v}

def _process_stacked_keys(node, subkeys, v):
    """Recurse over stacked entries and create nested objects.
    Print warning if schema mistmatch detected"""
    topkey = subkeys[0]
    _test = 0
    if topkey not in node:
        node[topkey] = {}
    elif type(node[topkey]) is not dict:
        old_value = node[topkey]
        node[topkey] = {}
        
        if topkey in SPECIAL_PARENT_DESCRIPTIONS:
            subkey = SPECIAL_PARENT_DESCRIPTIONS[topkey]
        else:
            warn("Stacked key doesn't match schema:\
                  <'{k}': {v}> already exists as <{old_k}: {old_v}>.\
                  Will be restacked as <'{old_k}:{old_k}': {old_v}>.\
                  Consider adding to special cases."\
                    .format(k=":".join(subkeys), v=v, old_k=topkey, old_v=old_value).replace("  ",""))
            subkey = topkey
        node[topkey][subkey] = old_value

    if len(subkeys) == 2:
        node[topkey][subkeys[1]] = v
    else:
        node[topkey] = _process_stacked_keys(node[topkey], subkeys[1:], v)
    
    return node
    
def _process_tags(node, kvs):
    """Add key value pair from tag to dictionary.
    Process stacked (k1:k2:k3...) entries recursively."""
    for kv in kvs:
    
        k = kv.attrib["k"]
        v = kv.attrib["v"]
        type = key_type(k)
        
        if type == "problemchars":
            continue
            
        elif type == "alphanum_colon":
            subkeys = k.split(":")
            topkey = subkeys[0]
            if topkey in SPECIAL_FUNCTIONS:
                parser = SPECIAL_FUNCTIONS[topkey]
                if parser is not None:
                    node = parser.update(node, k, v)
                else:
                    warn("Tag {} is a special tag, but no parser is implemented. Skipping."
                        .format(topkey))  
            else:
                node = _process_stacked_keys(node, subkeys, v)   
                
        else:
            if k in SPECIAL_FUNCTIONS:
                parser = SPECIAL_FUNCTIONS[k]
                if parser is not None:
                    node = parser.update(node, k, v)
                else:
                    warn("Tag {} is a special tag, but no parser is implemented. Skipping."
                        .format(k))                     
            else:
                node[k] = v
                
    return node
        
def _process_attrib(node, attrib):
    """Process attributes of every non-tag element"""
    if "lat" in attrib and "lon" in attrib:
        node["pos"] = [float(attrib["lat"]), float(attrib["lon"])]
    for k,v in attrib.items():
        if len(problemchars.findall(v)) > 0:
            continue
        if k in CREATED:
            if "created" not in node:
                node["created"] = {}
            node["created"][k] = v
        else:
            node[k] = v
    return node    
    
    
def _process_refs(node, refs, ref_name):
    """Helper to add all refs to an array"""
    node[ref_name] = []
    for ref in refs:
        try:
            node[ref_name].append(ref.attrib["ref"])
        except AttributeError:
            pass
    return node
    
def shape_element(element):
    """Convert each element to a dictionary object"""
    obj = {}
    obj["class"] = element.tag
    if obj["class"] in ["tag", "nd", "member"]:
        #tags, nd ref and memebers are processed within their parent
        return None
    if obj["class"] == "way":
        obj = _process_refs(obj, element.findall("nd"), "node_refs")
    if obj["class"] == "relation":
        obj = _process_refs(obj, element.findall("member"), "member_refs")
    
    obj = _process_attrib(obj, element.attrib)
    obj = _process_tags(obj, element.findall("tag"))
    
    return obj
    
    
    
def process_map(filename):
    """Iterate over XML file and execute operatons"""
    counted_keys = {"alphanum": defaultdict(int), "alphanum_colon": defaultdict(int), "problemchars": set(), "other": set()}
    tags = defaultdict(int)
    users = set()
    data = []
    for event, element in ET.iterparse(filename):
        #count tags
        tags[element.tag] += 1
        #count users
        if "uid" in element.attrib:
            users.add(get_user(element))
        #check for invalid key types
        counted_keys = count_key_type(element, counted_keys)
        obj = shape_element(element)
        if obj is not None:
            data.append(obj)
    

    return {"Summary":  {   "Tags": tags,
                            "Unique Keys": {k: len(v) for k, v in counted_keys.items()},
                            "Unique Users": len(users)
                        },
            "Data":     {   "Keys": counted_keys,
                            "JSON": data
                        }
            }
            
#from utils import display_circular_refs
#procedural
if __name__=="__main__":
    xml_file_name = "one-tenth.osm"
    stats = process_map(xml_file_name)
    pprint.pprint(stats["Summary"])
    single = find_fields_of_interest(stats["Data"]["Keys"]["alphanum"])
    stacked = find_fields_of_interest(stats["Data"]["Keys"]["alphanum_colon"])
    data = stats["Data"]["JSON"]
    pprint.pprint({"Single": single, "Stacked": stacked})
    #pprint.pprint(data)
    with codecs.open("parse_one_tenth.json", "w", encoding="utf-8") as log: 
        log.write(json.dumps(data, indent=2, ensure_ascii=False)+"\n")
    