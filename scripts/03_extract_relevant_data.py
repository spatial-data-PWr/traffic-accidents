import json
import pickle as pkl

import geopandas
import geopandas as gpd
import networkx as nx
from geojson import Point
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
