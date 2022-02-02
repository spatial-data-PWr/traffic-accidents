import os
import json
import requests 
import OSMPythonTools
from OSMPythonTools.overpass import overpassQueryBuilder
from src import STORAGE_PATH, TMP_PATH
from src.config import CITY

DATA_DIRECTORY = STORAGE_PATH / 'osm'

OUTPUT_FILENAME_PREFIX = 'osm_roads'

def create_selector(tag, values):
    result = f'"{tag}"~"'
    for highway_type in highway_types:
        result += highway_type + '|'
    result = result[0:-1] + '"'
    return result

highway_types = ['trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 
    'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link', 'living_street', 'road', 'bicycle', 'cycleway', 'path']

overpass = OSMPythonTools.overpass.Overpass()

area_q = 'area(id:3600451516)->.searchArea;'
highway_tags = '"highway"'#create_selector('highway', highway_types)
way_query = area_q + '(way[' + highway_tags + '](area.searchArea);); out body;'
node_query = area_q + '(way[' + highway_tags + '](area.searchArea);); node(w); out body;'

result_ways = overpass.query(way_query, timeout=120)
result_nodes = overpass.query(node_query, timeout=120)

if not os.path.exists(DATA_DIRECTORY):
    os.makedirs(DATA_DIRECTORY)

with open(DATA_DIRECTORY / f'{OUTPUT_FILENAME_PREFIX}_ways.json', 'w') as f:
    json.dump(result_ways.toJSON(), f)

with open(DATA_DIRECTORY / f'{OUTPUT_FILENAME_PREFIX}_nodes.json', 'w') as f:
    json.dump(result_nodes.toJSON(), f)
