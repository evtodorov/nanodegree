# -*- coding: utf-8 -*-
"""
From Udacity Sample OSM data project
"""


import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "41.6-24.7-42.3-26.0.osm"  # Replace this with your osm file
SAMPLE_FILE = "one-tenth.osm"

k = 10 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    # .encode() addded to fix erron on Python 3.6.10
    # TypeError: a bytes-like object is required, not 'str' 
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode())
    output.write('<osm>\n  '.encode())

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>'.encode())