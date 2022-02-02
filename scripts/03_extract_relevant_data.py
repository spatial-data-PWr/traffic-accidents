import json
import pickle as pkl

import geopandas
import geopandas as gpd
import networkx as nx
from geojson import Point, LineString
from pyproj import Transformer
from tqdm import tqdm

from src import STORAGE_PATH

DATA_DIRECTORY = STORAGE_PATH / 'data'
DATA_DIRECTORY.mkdir(exist_ok=True)

# Szczegóły zdarzeń
in_proj = 'epsg:2177'
out_proj = 'epsg:4326'
transformer = Transformer.from_crs(in_proj, out_proj)


Point()
SHAPEFILES_PATH = STORAGE_PATH / 'shapefiles'

accidents = []
for path in tqdm(
    list(SHAPEFILES_PATH.iterdir()),
    desc='Loading shapefiles',
):
    if path.is_file() and 'szczegoly_zdarzen' in path.name and path.suffix == '.shp':
        file_graph = nx.read_shp(str(path), strict=False)

        for (x, y), data in file_graph.nodes(data=True):
            y, x = transformer.transform(y, x)
            accidents.append(
                {
                    'geometry': Point((x, y)),
                    **data,
                }
            )

accidents_gdf = gpd.GeoDataFrame(accidents, geometry='geometry', crs=out_proj)
accidents_gdf.to_file(
    DATA_DIRECTORY.joinpath('accidents.geojson'),
    driver='GeoJSON',
)

# Trasy Rowerowe
bikepaths = geopandas.read_file(SHAPEFILES_PATH / 'TrasyRowerowe.shp', encoding='utf-8')
bikepaths = bikepaths[~bikepaths['geometry'].isna()]
bikepaths.crs = in_proj
bikepaths = bikepaths.to_crs(out_proj)
bikepaths.to_file(
    DATA_DIRECTORY.joinpath('bikeroads.geojson'),
    driver='GeoJSON',
)

# OSMRoads
OSM_DIRECTORY = STORAGE_PATH / 'osm'

with open(OSM_DIRECTORY / 'osm_roads_ways.json', 'r') as f:
    osm_data_ways = json.load(f)

with open(OSM_DIRECTORY / 'osm_roads_nodes.json', 'r') as f:
    osm_data_nodes = json.load(f)


node_map = {}
paths = []
for idx, element in enumerate(osm_data_nodes['elements']):
    node_map[element['id']] = {'point': (element['lon'], element['lat'])}

def tag_in_node(node, tag, values):
    return tag in node['tags'] and (element['tags'][tag] in values if values is not None else True)

def any_tag_in_node(node, tag):
    for n_tag in node['tags']:
        if tag in n_tag:
            return True
    return False

road_types = ['trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link', 'living_street', 'road', 'bicycle', 'cycleway']

for element in tqdm(osm_data_ways['elements'], desc='Converting OSM data to GeoJSON'):
    last_node = None
    path = {}
    path['bicycle'] = tag_in_node(element, 'bicycle', ['yes', 'use_sidepath', 'designated']) or element['tags']['highway'] == 'bicycle' or tag_in_node(element, 'oneway:bicycle', None)
    path['cycleway'] = any_tag_in_node(element, 'cycleway') or element['tags']['highway'] == 'cycleway' or tag_in_node(element, 'cyclestreet', None)
    path['oneway'] = tag_in_node(element, 'oneway', None)
    path['highway'] = element['tags']['highway']
    path['is_road'] = element['tags']['highway'] in road_types
    lines = []
    for node in element['nodes']:
        if node not in node_map:
            continue
        if last_node is not None:
            lines.append(LineString([node_map[last_node]['point'], node_map[node]['point']]))
        last_node = node

    path['tags'] = element['tags']

    for line in lines:
        path_c = path.copy()
        path_c['geometry'] = line
        paths.append(path_c)


osm_roads_gdf = gpd.GeoDataFrame(paths, geometry='geometry', crs=out_proj)
osm_roads_gdf.to_file(
    DATA_DIRECTORY.joinpath('osm_roads.geojson'),
    driver='GeoJSON',
)