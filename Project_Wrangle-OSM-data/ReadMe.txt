Submission checklist:
1. Wrangling OSM data.pdf
2. See "Code" below
3. osm-source.txt
4. one-tenth.osm
5. See "Sources" below

Data:
- Included:
one-tenth.osm		- Systematic sample of the OSM data produced by sample_file.py
- Not included:
41.6-24.7-42.3-26.0.osm - Open Street Map (OSM) XML data for a region in South Bulgaria to be processed.
SouthBG.json		- JSON conversion 
parse_one_tenth.json	- JSON conversion of the one-tenth.osm sample XML data

Code:
osm2json.py		- Routine to convert the OSM dataset to JSON and carry out cleaning and auditing
json2mongo.py		- Route to upload the converted OSM data to mongo databse "osm_data" at localhost 
parse_audit_clean.py	- Functions to parse, audit and clean the data
audit_address.py	- Functions to audit the address-associated fields in the data
audit_name.py		- Functions to audit the name-associated fields in the data
sample_file.py		- Routine to systematically sample every tenth element of an .osm file
Explore_OSM.py		- Jupyter notebook exported to python file, used for the data exploration

Sources:
https://www.openstreetmap.org/export#map=9/41.9843/25.3729
https://wiki.openstreetmap.org/wiki/
https://docs.python.org/3/library/json.html
https://docs.python.org/3/library/xml.etree.elementtree.html
https://docs.mongodb.com/manual/reference/
https://pymongo.readthedocs.io/en/stable/index.html
https://stackoverflow.com/questions/18337407/saving-utf-8-texts-in-json-dumps-as-utf8-not-as-u-escape-sequence
http://www.upu.int/fileadmin/documentsFiles/activities/addressingUnit/bgrEn.pdf
https://github.com/nimeshkverma/mongo_schema/