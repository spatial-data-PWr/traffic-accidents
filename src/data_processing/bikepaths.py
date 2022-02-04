import geopandas as gpd
import osmnx as ox


def get_graph_without_bikepaths(
    roads,
    trasy_rowerowe,
    min_road_to_bike_road_dist=10,
    max_relative_length=0.1,
):
    wide_lines = trasy_rowerowe['geometry'].buffer(min_road_to_bike_road_dist)
    wide_lines = gpd.GeoDataFrame(wide_lines, columns=['geometry'])

    wide_lines['_temp'] = 0
    wide_lines_shape = wide_lines.dissolve(by='_temp').iloc[0, 0]

    edges = ox.graph_to_gdfs(roads, nodes=False, edges=True)
    edges_geo = edges['geometry']
    relative_intersection_length = edges_geo.intersection(wide_lines_shape).length / edges_geo.length

    roads_without_bikeroad_index = edges[relative_intersection_length > max_relative_length].index

    roads_without_bikeroads = roads.copy()
    roads_without_bikeroads.remove_edges_from(roads_without_bikeroad_index)

    return roads_without_bikeroads
