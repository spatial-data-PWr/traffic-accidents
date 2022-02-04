import momepy
import networkx as nx
import osmnx as ox


def points_to_closest_edges(points, edges, max_dist=None):
    joined_points = points.to_crs('epsg:2180').sjoin_nearest(edges.to_crs('epsg:2180'), how='left', max_distance=max_dist)
    result = {}
    for _, p in joined_points.iterrows():
        edge = p['index_right']
        if edge == edge:
            if edge not in result:
                result[edge] = []
            result[edge].append(p)
    return result


def length_metric(edge, edge_points):
    return len(edge_points) / edge['geometry'].length


def count_metric(edge, edge_points):
    return len(edge_points)


def calculate_metric(points, edges, metric=count_metric, crs_to_convert=None, max_dist=None):
    edges_points = points_to_closest_edges(points, edges, max_dist)
    edges['metric'] = 0
    if crs_to_convert is not None:
        edges_in_crs = edges.to_crs(crs_to_convert)
    else:
        edges_in_crs = edges
    for edge in edges_points:
        edges.loc[edge, 'metric'] = metric(edges_in_crs.loc[edge], edges_points[edge])


def compute_danger_metric(
    roads_without_bikeroads,
    roads,
    bike_accidents,
    target_crs='EPSG:2180',
    number_of_accidents_weight=0.7,
    continuity_weight=0.1,
    maxspeed_weight=0.1,
    betweenes_weight=0.1,
):
    maxspeeds = get_maxspeeds(roads)
    continuity = compute_continuity_metric(roads)
    betweenes = compute_betweeness(roads)

    edges = ox.graph_to_gdfs(roads_without_bikeroads, nodes=False, edges=True).reset_index()
    calculate_metric(bike_accidents, edges, crs_to_convert=target_crs, max_dist=20)
    edges = edges.set_index(['u', 'v', 'key'])
    edges['metric'] /= edges['metric'].max()
    number_of_accidents = edges['metric'].to_dict()

    return {
        idx: (
            number_of_accidents[idx] * number_of_accidents_weight +
            maxspeeds[idx] * maxspeed_weight +
            continuity.get(idx, 0) * continuity_weight +
            betweenes.get((idx[0], idx[1]), betweenes.get((idx[1], idx[0]), 0)) * betweenes_weight
        ) for idx in edges.index
    }


def compute_continuity_metric(
    roads,
):
    roads_gdf = ox.graph_to_gdfs(
        ox.get_undirected(roads),
        nodes=False, edges=True,
        node_geometry=False, fill_edge_geometry=True
    )
    continuity = momepy.COINS(roads_gdf)
    stroke_gdf = continuity.stroke_gdf()
    cont = stroke_gdf.length / stroke_gdf.length.max()
    edge_to_continuity = {
        (r['u'], r['v'], r['key']): cont[r[0]]
        for _, r in continuity.stroke_attribute().reset_index().iterrows()
    }
    return edge_to_continuity


def get_maxspeeds(roads):
    def sanitize(maxspeed):
        if isinstance(maxspeed, list):
            maxspeed = maxspeed[0]
        if maxspeed is None:
            maxspeed = 50

        return int(maxspeed) if isinstance(maxspeed, str) else 50

    edges = ox.graph_to_gdfs(roads, edges=True, nodes=False)

    maxspeeds = {
        (r['u'], r['v'], r['key']): sanitize(r['maxspeed']) for _, r in edges.reset_index().iterrows()
    }
    max_maxspeed = max(maxspeeds.values())
    return {k: v / max_maxspeed for k, v in maxspeeds.items()}


def compute_betweeness(roads):
    betweenness = nx.edge_betweenness_centrality(roads, k=1000)
    max_btw = max(betweenness.values())
    return {k: v / max_btw for k, v in betweenness.items()}
