import os
import json
import requests 
import OSMPythonTools
from OSMPythonTools.overpass import overpassQueryBuilder
from src.config import CITY, DATA_DIRECTORY, TEMP_DIRECTORY

OUTPUT_FILENAME_PREFIX = 'osm_roads'

def create_selector(tag, values):
    result = f'"{tag}"~"'
    for highway_type in highway_types:
        result += highway_type + '|'
    result = result[0:-1] + '"'
    return result

nominatim = OSMPythonTools.nominatim.Nominatim()
overpass = OSMPythonTools.overpass.Overpass()

area_id = nominatim.query(CITY).areaId()
highway_types = ['trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 
    'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link', 'living_street', 'road']

query = overpassQueryBuilder(area=area_id, elementType='way', selector=[create_selector('highway', highway_types)], out='body')
result_ways = overpass.query(query, timeout=120)

query = overpassQueryBuilder(area=area_id, elementType='way', selector=[create_selector('highway', highway_types)], out='body').replace(' out body;', '') + 'node(w); out body;'
result_nodes = overpass.query(query, timeout=120)

with open(f'{DATA_DIRECTORY}/{OUTPUT_FILENAME_PREFIX}_ways.json', 'w') as f:
    json.dump(result_ways.toJSON(), f)

with open(f'{DATA_DIRECTORY}/{OUTPUT_FILENAME_PREFIX}_nodes.json', 'w') as f:
    json.dump(result_nodes.toJSON(), f)