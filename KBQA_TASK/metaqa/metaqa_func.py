import json
import pandas as pd
import re
from prompt_list import *
import pdb
import openai

def write_to_file(filename, data):
    with open(filename, 'a',encoding='utf-8') as file:
        file.write(data + '\n')
        print("Data written to file")
        
def expand_path(kg,path_set):
    if not path_set:
        return path_set
    if(len(list(path_set.items())[0][1]) % 2 == 1):
        expand_paths = []
        for path_key,path_value in path_set.items():
            tail_entity = path_value[-1]
            if tail_entity in kg:
                expand_relation_set = kg[tail_entity]
                expand_relation_list = list(expand_relation_set.keys())
                expand_paths.extend([(path_value + [item,]) for item in expand_relation_list])
            expand_path_dict = {}
            for i, path in enumerate(expand_paths):
                expand_path_dict[f"path_{i + 1}"] = path
    else:
        expand_paths = []
        for path_key,path_value in path_set.items():
            tail_entity,tail_relation = path_value[-2],path_value[-1]
            if tail_entity in kg:
                expand_entity_list = kg[tail_entity][tail_relation]
                for item in expand_entity_list:
                    if item not in path_value:
                        expand_paths.extend([path_value + [item,]])
        expand_path_dict = {}
        for i, path in enumerate(expand_paths):
            expand_path_dict[f"path_{i + 1}"] = path
    return expand_path_dict


def expand_path_new(kg,path_set,entity_set):
    if not path_set:
        return path_set
    if(len(list(path_set.items())[0][1]) % 2 == 1):
        expand_paths = []
        for path_key,path_value in path_set.items():
            tail_entity = path_value[-1]
            if tail_entity in kg:
                expand_relation_set = kg[tail_entity] 
                expand_relation_list = list(expand_relation_set.keys()) 
                expand_paths.extend([(path_value + [item,]) for item in expand_relation_list])
            expand_path_dict = {}
            for i, path in enumerate(expand_paths):
                expand_path_dict[f"path_{i + 1}"] = path
    else:
        expand_paths = []
        for path_key,path_value in path_set.items():
            tail_entity,tail_relation = path_value[-2],path_value[-1]
            if tail_entity in kg:
                expand_entity_list = kg[tail_entity][tail_relation]
                for item in expand_entity_list:
                    if item not in entity_set:
                        expand_paths.extend([path_value + [item,]])
                        entity_set.append(item)
        expand_path_dict = {}
        for i, path in enumerate(expand_paths):
            expand_path_dict[f"path_{i + 1}"] = path
    return expand_path_dict,entity_set
def get_rel_set(kg,head_entity_set):
    rel_set = set()
    for head_entity in head_entity_set:
        if head_entity in kg:
            rel_set = rel_set.union(kg[head_entity])
            rel_set.discard("~release_year")
    return rel_set

def get_tail_entity_set(kg, head_entity_set, best_rel):
    tail_entity_set = set() 
    for head_entity in head_entity_set:
        if head_entity in kg:
            try:
                tail_entity_set = tail_entity_set.union(kg[head_entity][best_rel])
            except KeyError:
                continue  
    return tail_entity_set