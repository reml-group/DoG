from SPARQLWrapper import SPARQLWrapper, JSON
import pdb
SPARQLPATH = "http://localhost:8890/sparql"  

# pre-defined sparqls
sparql_head_relations = """\nPREFIX ns: <http://rdf.freebase.com/ns/>\nSELECT ?relation\nWHERE {\n  ns:%s ?relation ?x .\n}"""
sparql_tail_relations = """\nPREFIX ns: <http://rdf.freebase.com/ns/>\nSELECT ?relation\nWHERE {\n  ?x ?relation ns:%s .\n}"""
sparql_tail_entities_extract = """PREFIX ns: <http://rdf.freebase.com/ns/>\nSELECT ?tailEntity\nWHERE {\nns:%s ns:%s ?tailEntity .\n}""" 
sparql_head_entities_extract = """PREFIX ns: <http://rdf.freebase.com/ns/>\nSELECT ?tailEntity\nWHERE {\n?tailEntity ns:%s ns:%s  .\n}"""
sparql_id = """PREFIX ns: <http://rdf.freebase.com/ns/>\nSELECT DISTINCT ?tailEntity\nWHERE {\n  {\n    ?entity ns:type.object.name ?tailEntity .\n    FILTER(?entity = ns:%s)\n  }\n  UNION\n  {\n    ?entity <http://www.w3.org/2002/07/owl#sameAs> ?tailEntity .\n    FILTER(?entity = ns:%s)\n  }\n}"""
sparql_el_extract = """PREFIX ns: <http://rdf.freebase.com/ns/>\nSELECT ?ent\nWHERE {\n?ent ns:type.object.name "Taiwan"@en .\n}"""

def write_to_file(filename, data):
    with open(filename, 'a',encoding='utf-8') as file:
        file.write(data + '\n')
        print("Data written to file")

def abandon_rels(relation):
    if relation == "type.object.type" or relation == "type.object.name" or relation =="user.narphorium.people.nndb_person.nndb_id" or relation.startswith("common.") or  relation.startswith("kg.") or relation.startswith("freebase.") or "sameAs" in relation:
        return True


def execurte_sparql(sparql_query):
    sparql = SPARQLWrapper(SPARQLPATH)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return results["results"]["bindings"]
    except:
        return []


def replace_relation_prefix(relations):
    return [relation['relation']['value'].replace("http://rdf.freebase.com/ns/","") for relation in relations]

def replace_entities_prefix(entities):
    return [entity['tailEntity']['value'].replace("http://rdf.freebase.com/ns/","") for entity in entities]


def id2entity_name_or_type(entity_id):
    sparql_query = sparql_id % (entity_id, entity_id)
    sparql = SPARQLWrapper(SPARQLPATH)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
    except:
        return "UnName_Entity"
    if len(results["results"]["bindings"])==0:
        return "UnName_Entity"
    else:
        try:
            return results["results"]["bindings"][0]['tailEntity']['value']
        except:
            return "UnName_Entity"
    
from freebase_func import *
from prompt_list import *
import json
import time
import openai
import re
from prompt_list import *

def relation_search(entity_id):
    sparql_relations_extract_head = sparql_head_relations % (entity_id)
    head_relations = execurte_sparql(sparql_relations_extract_head)
    head_relations = replace_relation_prefix(head_relations)
    head_relations = [relation for relation in head_relations if not abandon_rels(relation)]
    head_relations = list(set(head_relations))
    return head_relations


def get_rel_list(head_entity_set):
    total_rel_list = []
    for ent_id,_ in head_entity_set:
        total_rel_list = total_rel_list+relation_search(ent_id)
    return total_rel_list

    
    
def entity_search(entity, relation, head=True):
    if head:
        tail_entities_extract = sparql_tail_entities_extract% (entity, relation)
        entities = execurte_sparql(tail_entities_extract)
    else:
        head_entities_extract = sparql_head_entities_extract% (entity, relation)
        entities = execurte_sparql(head_entities_extract)


    entity_ids = replace_entities_prefix(entities)
    new_entity = [entity for entity in entity_ids]
    return new_entity

def get_tail_entity_dict_set(head_entity_dict_set,best_rel,all_unknow):
    if all_unknow:
        tail_ent_id_list = []
        for ent_id,_ in head_entity_dict_set:
            tail_ent_id_list = tail_ent_id_list+list(set(entity_search(ent_id,best_rel)))
        tail_entity_dict_set = []
        for ent_id in tail_ent_id_list:
            if id2entity_name_or_type(ent_id) !=  "UnName_Entity" :
                tail_entity_dict_set.append((ent_id,id2entity_name_or_type(ent_id)))
        return tail_entity_dict_set
    else:
        tail_ent_id_list = []
        for ent_id,_ in head_entity_dict_set:
            tail_ent_id_list = tail_ent_id_list+list(set(entity_search(ent_id,best_rel)))
        tail_entity_dict_set = []
        for ent_id in tail_ent_id_list:
            if id2entity_name_or_type(ent_id) !=  "UnName_Entity" :
                tail_entity_dict_set.append((ent_id,id2entity_name_or_type(ent_id)))
            
        return tail_entity_dict_set

def get_reasoning_triple_list(head_entity_dict_set,best_rel,all_unknow):
    if all_unknow:
        reasoning_triple_list = []
        for ent_id,ent_name in head_entity_dict_set:
            tail_entity_id_list = list(set(entity_search(ent_id,best_rel)))
            for tail_entity_id in tail_entity_id_list:
                temp_set = []
                temp_set.append((tail_entity_id, "test"))
                new_rel_list = get_rel_list(temp_set)
                for new_rel in new_rel_list:
                    new_tail_entity_id_list = list(set(entity_search(tail_entity_id,new_rel)))
                    for new_tail_entity_id in new_tail_entity_id_list:
                        new_tail_entity_name = id2entity_name_or_type(new_tail_entity_id)
                        new_triple = (ent_name,best_rel,tail_entity_id,new_rel,new_tail_entity_name)
                        reasoning_triple_list.append(new_triple)
        return reasoning_triple_list
    else: 
        reasoning_triple_list = []
        for ent_id,ent_name in head_entity_dict_set:
            tail_entity_id_list = list(set(entity_search(ent_id,best_rel)))
            for tail_entity_id in tail_entity_id_list:
                if id2entity_name_or_type(tail_entity_id) !=  "UnName_Entity" :
                    tail_entity_name = id2entity_name_or_type(tail_entity_id) 
                    new_triple = (ent_name,best_rel,tail_entity_name)
                    reasoning_triple_list.append(new_triple)
        return reasoning_triple_list