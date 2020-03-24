# contains helper functions for app code

import json

def index_in_lists_of_dicts(lists,key,value):
    '''
    checks lists to see if a key value exists in it
    returns the list and index of the first dict where the key and 
    value was found, else returns None,None

    none: index 0 can be returned, so use explicit tests with result
    '''
    for l in lists:
        for index, d in enumerate(l):
            if d[key] == value:
                return l,index
    return None,None

def index_in_list_of_dicts(list_to_check,key,value):
    '''
    searches a list to see if a dict with a key value exists in it
    returns the index of the first dict where the key and 
    value pair is found, else returns None

    none: index 0 can be returned, so use explicit tests with result
    '''
    for index, d in enumerate(list_to_check):
        if d[key] == value:
            return index
    return None

def json_load(filename):
    '''returns contents of JSON file'''
    with open(filename) as json_file: 
        return json.load(json_file)

def json_update(data, filename):
    '''
    updates dict in JSON file
    @data dict: data to update json dict
    @filename str: JSON file path containing dict to update
    '''
    tmp = json_load(filename)
    tmp.update(data)
    with open(filename,'w') as json_file:
        json.dump(tmp, json_file)

def initialize_json(data, filename):
    '''
    create a new JSON file with data
    @data JSON data: to initialize file with 
    @ filename str: path of file
    '''
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)

def search_array_for_dict_with_key(s_array,key):
    '''
    returns False if dict is not found in array
    otherwise returns array index
    note: index 0 can be returned, so use explicit tests with result
    '''
    return next((i for i,item in enumerate(s_array) if key in item), False)

def unpack_keys_from_array_of_dicts(array_of_dicts):
    '''return all keys from an array of dicts'''
    keys = []
    for k in array_of_dicts:
        keys.append(*k)
    return keys

