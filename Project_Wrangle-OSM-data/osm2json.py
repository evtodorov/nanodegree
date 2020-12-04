# -*- coding: utf-8 -*-
from parse_audit_clean import process_map
import json, codecs, pprint

xml_file_name = "41.6-24.7-42.3-26.0.osm"
json_file_name = "SouthBG.json"

if __name__=="__main__":
    stats = process_map(xml_file_name)
    pprint.pprint(stats["Summary"])
    data = stats["Data"]["JSON"]

    with codecs.open(json_file_name, "w", encoding="utf-8") as log: 
        log.write(json.dumps(data, ensure_ascii=False)+"\n")