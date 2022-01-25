import os
import json
import pickle as pkl
import requests
import networkx as nx
import geopandas
import OSMPythonTools
from OSMPythonTools.overpass import overpassQueryBuilder
from src import STORAGE_PATH, TMP_PATH
from src.config import CITY

DATA_DIRECTORY = STORAGE_PATH / 'graphs'

# Szczegóły zdarzeń

SHAPEFILES_PATH = STORAGE_PATH / 'shapefiles'

accidents_graph = None
for filename in os.listdir(SHAPEFILES_PATH):
    path = SHAPEFILES_PATH / filename
    if os.path.isfile(path) and 'szczegoly_zdarzen' in filename and '.shp' in filename:
        file_graph = nx.read_shp(str(path), strict=False)
        if accidents_graph is None:
            accidents_graph = file_graph
        else:
            accidents_graph = nx.compose(accidents_graph, file_graph)

unknown_accidents = []
bike_accidents = []
nonbike_accidents = []
for node in accidents_graph.nodes(data=True):
    if 'POJ_ROWER' in node[1] and node[1]['POJ_ROWER'] > 0.0:
        bike_accidents.append(node[0])
    else:
        nonbike_accidents.append(node[0])

bike_accidents_graph = accidents_graph.copy()
nonbike_accidents_graph = accidents_graph.copy()

for node in nonbike_accidents:
    bike_accidents_graph.remove_node(node)

for node in bike_accidents:
    nonbike_accidents_graph.remove_node(node)

if not os.path.exists(DATA_DIRECTORY):
    os.makedirs(DATA_DIRECTORY)

with open(DATA_DIRECTORY / 'bike_accidents_graph.pkl', 'wb') as f:
    pkl.dump(bike_accidents_graph, f)

with open(DATA_DIRECTORY / 'nonbike_accidents_graph.pkl', 'wb') as f:
    pkl.dump(nonbike_accidents_graph, f)

# Trasy Rowerowe

bikepaths = geopandas.read_file(SHAPEFILES_PATH / 'TrasyRowerowe.shp', encoding='utf-8')
bikepaths = bikepaths.drop(bikepaths[bikepaths['geometry'].isnull()].index)
bikepaths = bikepaths.drop(bikepaths[bikepaths['TYP'] == 'strefa ruchu uspokojonego 20 i 30 km/h'].index)

with open(DATA_DIRECTORY / 'bikepaths.pkl', 'wb') as f:
    pkl.dump(bikepaths, f)

# OSMRoads

OSM_DIRECTORY = STORAGE_PATH / 'osm'

with open(OSM_DIRECTORY / 'osm_roads_ways.json', 'r') as f:
    osm_data_ways = json.load(f)

with open(OSM_DIRECTORY / 'osm_roads_nodes.json', 'r') as f:
    osm_data_nodes = json.load(f)

osm_graph = nx.Graph()
nodes = {}
for idx, element in enumerate(osm_data_nodes['elements']):
    nodes[element['id']] = {'index': idx, 'data': (element['lat'], element['lon'])}
    osm_graph.add_node(idx, location=(element['lat'], element['lon']))

for element in osm_data_ways['elements']:
    last_node = None
    for node in element['nodes']:
        if last_node is not None:
            osm_graph.add_edge(last_node, node, data=element['tags'])
        last_node = node

with open(DATA_DIRECTORY / 'osm_roads_graph.pkl', 'wb') as f:
    pkl.dump(osm_graph, f)
