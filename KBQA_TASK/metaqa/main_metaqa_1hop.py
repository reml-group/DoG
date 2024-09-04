import os
import json
import pickle
import jsonlines
import openai
import re
import random
import requests
import sys
from eval_helper.get_evaluation import get_evaluation
from agentverse.agentverse import AgentVerse
from argparse import ArgumentParser

from metaqa_func import *
from prompt_list import *

parser = ArgumentParser()


parser.add_argument("--task", type=str, default="kgqa/freebase/one_role_one_turn_sequential_freebase")
parser.add_argument("--output_path",type=str, default = "")
args = parser.parse_args()

if __name__ =="__main__":
    
    with open('./data/metaqa_kg.pickle', 'rb') as f:
        kg = pickle.load(f)
    print('Data loading done!!!')
    
    agentverse = AgentVerse.from_task(args.task)

    correct_num = 0
    wrong_num = 0
    output_path = args.output_path
    with open(os.path.expanduser(f"./data/threehop_test_set.jsonl"),encoding='utf-8') as f:
        for line in f:
            if not line:
                continue
            q = json.loads(line)
            error = 0
            start_entity = q["entity_set"][0]
            path_set = {}
            path_set["path_1"] = [start_entity]
            question_id = q["question_id"]
            write_to_file(output_path,f"====================question_id: {question_id}====================")
            question = q["question"]
            write_to_file(output_path,f"origin_question: {question}")    
            write_to_file(output_path,f"path_set: {path_set}")
            flag = 0
            head_entity_list = []
            head_entity_list.append(start_entity)
            for i in range (3):
                relation_set = get_rel_set(kg,set(head_entity_list))
                write_to_file(output_path,f"relation_set: {relation_set}")
                mapping_rel_dict = {f'relation_{i+1}': item for i, item in enumerate(relation_set)}
                mapping_rel_string = ', '.join(f"{key}: {value}" for key, value in mapping_rel_dict.items())
                write_to_file(output_path,f"relation_set: {mapping_rel_string}")
                input_text = filter_best_rel_prompt +f"""question:{question}
relation_set:{mapping_rel_string}"""
                chatgpt_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-0125",  
                    messages=[
                        {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                        {"role": "user", "content": input_text}
                    ],
                    max_tokens=150,  
                )           
                    
                generated_answer = chatgpt_response['choices'][0]['message']['content']
                # get best_rel
                write_to_file(output_path,f"generated_answer: {generated_answer}")
                pattern = r'relation_\d+'   
                matches = re.findall(pattern, generated_answer,re.IGNORECASE)
                best_rel_list = []
                if len(matches) != 0:
                    try:
                        for match in matches:
                            best_rel_list.append(mapping_rel_dict[match.lower()])
                    except:
                        error = 1
                        break 
                else:
                    flag = 0
                    for value in mapping_rel_dict.values():
                        if value in generated_answer:
                            best_rel_list.append(value)
                            flag = 1
                    if flag == 0:
                        error = 1
                        break
                best_rel_list = list(set(best_rel_list))
                write_to_file(output_path,f"best_relation: {best_rel_list}")
                reasoning_path = []
                tail_entity_set = set()
                tail_entity_list = []
                for best_rel in best_rel_list:
                    tail_entity_set = get_tail_entity_set(kg,set(head_entity_list),best_rel)
                    tail_entity_list = tail_entity_list + list(tail_entity_set)
                    if(best_rel[0] == '~'):
                        result_string ="("+ tail_entity_list[0]+","+best_rel[1:]+","+ head_entity_list[0]+")"
                    else:
                        result_string ="("+ head_entity_list[0]+","+best_rel+","+ tail_entity_list[0]+")"
                    reasoning_path.append(result_string)
                    break 
                write_to_file(output_path,f"entity_set: {tail_entity_list}")
                if(i != 0): # 无跳数信息，判断当前信息是否足够回答问题
                    write_to_file(output_path,f"path: {reasoning_path}")
                    for agent_id in range(len(agentverse.agents)):
                        agentverse.agents[agent_id].source_text = "Problems that need to be simplified:"+question
                        agentverse.agents[agent_id].compared_text_one = reasoning_path
                        agentverse.agents[agent_id].final_prompt = ""
                    done = 0
                    time = 0
                    agentverse.run()
                    time = time + 1
                    evaluation = get_evaluation(setting="every_agent", messages=agentverse.agents[0].memory.messages, agent_nums=len(agentverse.agents))
                    question = evaluation[len(agentverse.agents)-1]['evaluation']
                    colon_index = question.find(":") 
                    if colon_index != -1:  
                        question = question[colon_index + 1:].strip()  
                    write_to_file(output_path,f"question: {question}")
                head_entity_list = tail_entity_list
            if error:
                continue
            corresponding_answer = q["Label"]
            intersection = set(head_entity_list).intersection(set(corresponding_answer))
            if intersection:
                write_to_file(output_path,f"correct!\n")
                correct_num = correct_num + 1
            else:
                write_to_file(output_path,f"wrong!\n")
                wrong_num = wrong_num + 1
        accuracy = (correct_num / (correct_num + wrong_num)) * 100
        write_to_file(output_path,f"{accuracy:.1f}%")