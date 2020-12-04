# -*- coding: utf-8 -*-
import json, codecs, os


if __name__ == "__main__":
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    
    json_file_name = "SouthBG.json"
    db = client.osm_data

    with codecs.open(json_file_name, "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        db[os.path.splitext(os.path.basename(json_file_name))[0]].insert(data, db)