import matplotlib.colors
import folium
def convert_dict_list_to_counts_dataframe(dict_list):
    result = {'names' : [], 'counts' : []}
    for d in dict_list:
        result['names'].append(d)
        result['counts'].append(len(dict_list[d]))
    return result


def interpolate(minimum, current, maximum, c1, c2, mid_color=None, mid_value=None):
    if mid_color is not None and mid_value is not None:
        if mid_value < current:
            return interpolate(mid_value, current, maximum, mid_color, c2)
        else:
            return interpolate(minimum, current, mid_value, c1, mid_color)
        
    if current > maximum:
        current = maximum
    w = (current - minimum) / (maximum - minimum)

    return int(c2[0]*w + c1[0]*(1-w)), int(c2[1]*w + c1[1]*(1-w)), int(c2[2]*w + c1[2]*(1-w)) 

def create_smooth_choropleth_layers(dataframe, key_column_name, count_column_name, geo_data, geo_data_key, beg_color, end_color, mid_color=None, force_min=None, force_mid=None, force_max=None):
    beg_color = matplotlib.colors.to_rgb(beg_color)
    beg_color = beg_color[0] * 255, beg_color[1] * 255, beg_color[2] * 255

    end_color = matplotlib.colors.to_rgb(end_color)
    end_color = end_color[0] * 255, end_color[1] * 255, end_color[2] * 255

    if mid_color is not None:
        mid_color = matplotlib.colors.to_rgb(mid_color)
        mid_color = mid_color[0] * 255, mid_color[1] * 255, mid_color[2] * 255

    maximum_active = force_max
    minimum_active = force_min

    if force_min is None or force_max is None:
        for _, row in dataframe.iterrows():
            if row[count_column_name] != row[count_column_name]:
                continue
            if maximum_active is None or row[count_column_name] > maximum_active:
                maximum_active = row[count_column_name]
            if minimum_active is None or row[count_column_name] < minimum_active:
                minimum_active = row[count_column_name]
    result = []
    for _, row in dataframe.iterrows():
        sub_geojson = geo_data.copy()
        region = row[key_column_name]
        sub_geojson['features'] = sub_geojson['features'].copy()
        to_delete = []
        for gd_region in sub_geojson['features']:
            if geo_data_key(gd_region) != region:
                to_delete.append(gd_region)
        for t_d in to_delete:
            sub_geojson['features'].remove(t_d)
        if len(sub_geojson['features']) == 0 or row[count_column_name] != row[count_column_name]:
            continue
        color_tuple = interpolate(minimum_active, row[count_column_name], maximum_active, beg_color, end_color, mid_color=mid_color, mid_value=force_mid)
        
        color = f'#{color_tuple[0]:0>2x}{color_tuple[1]:0>2x}{color_tuple[2]:0>2x}'
        result.append(folium.Choropleth(
            geo_data=sub_geojson,
            name="choropleth",
            fill_color=color,
            fill_opacity=1.0,
            line_opacity=0.0,
            smooth_factor=0.2
        ))
    return result
