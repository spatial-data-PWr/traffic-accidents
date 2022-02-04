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