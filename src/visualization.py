def convert_dict_list_to_counts_dataframe(dict_list):
    result = {'names' : [], 'counts' : []}
    for d in dict_list:
        result['names'].append(d)
        result['counts'].append(len(dict_list[d]))
    return result