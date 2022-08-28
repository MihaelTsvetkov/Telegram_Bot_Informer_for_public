def convert_list_for_int_and_float(list_of_tuples):
    list_of_listet = []
    list_tuple = list(list_of_tuples)
    for items in list_tuple:
        list_items = list(items)
        clear_items = list_items[0]
        int_items = int(clear_items)
        list_of_listet.append(int_items)
    return list_of_listet


def convert_list_for_other_types(list_of_tuples):
    output = []
    list_tuple = list(list_of_tuples)
    for items in list_tuple:
        list_items = list(items)
        clear_items = list_items[0]
        output.append(clear_items)
    return output


def output_sources_and_topics(d: dict):
    output = []
    if d:
        for source in d.keys():
            list_of_topics = d[source]
            output.append(source + ': ' + ','.join(list_of_topics) + "\n")
        return ''.join(output)
    else:
        return output
