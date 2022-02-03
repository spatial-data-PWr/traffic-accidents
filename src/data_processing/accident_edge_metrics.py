def points_to_closest_edges(points, edges, max_dist=None):
    joined_points = points.to_crs('epsg:2177').sjoin_nearest(edges.to_crs('epsg:2177'), how='left', max_distance=max_dist)
    result = {}
    for _, p in joined_points.iterrows():
        edge = p['index_right']
        if edge not in result:
            result[edge] = []
        result[edge].append(p)
    return result

# def __ptce_newer(points, edges, max_dist=0.01): #Only for the record
#     result = {}
#     points_s = MultiPoint(points)
#     points_arr = {}
#     for ind, edge in enumerate(tqdm(edges)):
#         edge_rect = edge.buffer(max_dist)
#         points_t = edge_rect.union(points_s)
#         for point in points_t:
#             if type(point) is not Point:
#                 continue
#             if point.coords not in points_arr:
#                 points_arr[point.coords] = ind
#             elif point.distance(edge) < point.distance(edges[points_arr[point.coords]]):
#                  points_arr[point.coords] = ind
    
#     for point_coords in tqdm(points_arr):
#         if points_arr[point_coords] not in result:
#             result[points_arr[point_coords]] = []
#         result[points_arr[point_coords]].append(Point(point_coords))
#     return result


# def __ptce_old(points, edges, max_dist): #Only for the record
#     result = {}
#     for point in tqdm(points):
#         min_edge_ind, min_dist = None, None
#         for ind, edge in enumerate(edges):
#             if edge.representative_point().distance(point) < max_dist:
#                 dist = point.distance(edge)
#                 if min_dist is None or min_dist > dist:
#                     min_edge_ind, min_dist = ind, dist
#         if min_edge_ind is not None:
#             if ind not in result:
#                 result[ind] = []
#             result[ind].append(point)
#     return result


# def __length_metric_df(edge): #Only for the record
#     return len(edge['geometry']) / edge['old_geometry'].length


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