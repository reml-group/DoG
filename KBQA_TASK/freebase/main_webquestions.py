import os
import json
import pdb
import openai
import re
from eval_helper.get_evaluation import get_evaluation
from agentverse.agentverse import AgentVerse
from argparse import ArgumentParser

from freebase_func import *
from prompt_list import *

parser = ArgumentParser()

parser.add_argument("--task", type=str, default="")
parser.add_argument("--output_path",type=str, default = "")
args = parser.parse_args()

if __name__ =="__main__":
        
    agentverse = AgentVerse.from_task(args.task)

    correct_num = 0
    wrong_num = 0
    output_path = args.output_path
    file_path = "./dataset/WebQuestions.json" 
    with open(os.path.expanduser(file_path), encoding='utf-8') as f:
        json_data = json.load(f)
    question_num = 0
    max_turn = 3
    for q in json_data:
        if not q:
            continue
        write_to_file(output_path,f"==================={question_num}========================")
        question = q["question"]
        origin_question = question
        error = 0
        need_LLM = 0
        start_entity = list(q["topic_entity"].items())[0] 
        write_to_file(output_path,f"origin_question: {question}")    
        head_entity_dict_set = []
        head_entity_dict_set.append(start_entity)
        for i in range (max_turn):
            write_to_file(output_path,f"head_entity: {head_entity_dict_set}")  
            relation_list = get_rel_list(head_entity_dict_set)
            write_to_file(output_path,f"relation_set: {relation_list}")
            mapping_rel_dict = {f'relation_{i+1}': item for i, item in enumerate(relation_list)}
            mapping_rel_string = ', '.join(f"{key}: {value}" for key, value in mapping_rel_dict.items())
            write_to_file(output_path,f"relation_set: {mapping_rel_string}")
            input_text = filter_best_rel_prompt +f"""Q:{question}
Relations:{mapping_rel_string}
A:"""
            chatgpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0125",  
                messages=[
                    {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                    {"role": "user", "content": input_text}
                ],
                max_tokens=150, 
            )                
            generated_answer = chatgpt_response['choices'][0]['message']['content']
            write_to_file(output_path,f"generated_answer: {generated_answer}")
            pattern = r'relation_\d+'
            matches = re.findall(pattern, generated_answer,re.IGNORECASE)
            best_rel_list = []
            if matches is None:
                for key, value in mapping_rel_dict.items():
                    if value in generated_answer:
                        best_rel_list.append(mapping_rel_dict[key])
                if not best_rel_list:
                    error = 1
                    break
            else:
                for match in matches:
                    try:
                        best_rel_list.append(mapping_rel_dict[match.lower()])
                    except:
                        error = 1
                        break
            if not best_rel_list:
                error = 1
                break
            tail_entity_dict_set = []
            reasoning_triple_list = []
            best_rel_list = list(set(best_rel_list))
            write_to_file(output_path,f"best_relation: {best_rel_list}")
            for best_rel in best_rel_list:
                if not get_tail_entity_dict_set(head_entity_dict_set,best_rel,False):
                    tail_entity_dict_set += get_tail_entity_dict_set(head_entity_dict_set,best_rel,True)
                    try:
                        reasoning_triple_list += get_reasoning_triple_list(head_entity_dict_set,best_rel,True)
                    except:
                        pass
                else:
                    tail_entity_dict_set += get_tail_entity_dict_set(head_entity_dict_set,best_rel,False)
                    reasoning_triple_list += get_reasoning_triple_list(head_entity_dict_set,best_rel,False)
            enough_ans = 0
            path_count = 1
            output_str = ""
            for triple in reasoning_triple_list:
                path_str = f"path_{path_count}: {triple}, "
                output_str += path_str
                path_count += 1
            output_str = output_str[:-2]
            write_to_file(output_path,f"path: {output_str}")
            input_text = enough_ans_prompt +f"""Q:{question}
Knowledge Triplets:{output_str}"""
            chatgpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0125", 
                messages=[
                    {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                    {"role": "user", "content": input_text}
                ],
                max_tokens=150,  
            )                
            generated_answer = chatgpt_response['choices'][0]['message']['content']
            write_to_file(output_path,f"generated_answer:{generated_answer}")
            match = re.search(r'\bYes\b', generated_answer,re.I)
            if match:
                break
            if(i == max_turn-1):  
                need_LLM = 1
                break
            if(i != max_turn-1):
                for agent_id in range(len(agentverse.agents)):
                    agentverse.agents[agent_id].source_text = question
                    agentverse.agents[agent_id].compared_text_one = output_str
                    agentverse.agents[agent_id].final_prompt = ""
                agentverse.run()
                
                evaluation = get_evaluation(setting="every_agent", messages=agentverse.agents[0].memory.messages, agent_nums=len(agentverse.agents))
                question = evaluation[len(agentverse.agents)-1]['evaluation']
                write_to_file(output_path,f"question: {question}")
            head_entity_dict_set = tail_entity_dict_set
        answer_list = q["answers"]
        find = 0
        if not need_LLM:
            try:
                generated_answer_processed = generated_answer.replace(" ", "").lower()
                processed_list = [answer.replace(" ", "").lower() for answer in answer_list]
                for item in processed_list:
                    if item in generated_answer_processed:
                        find = 1
                        break
            except:
                find = 0
        if need_LLM or not find:
            input_text = f"""Q:{origin_question}"""
            chatgpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0125",  
                messages=[
                    {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                    {"role": "user", "content": input_text}
                ],
                max_tokens=150,  
            )                
            generated_answer = chatgpt_response['choices'][0]['message']['content']
        generated_answer_processed = generated_answer.replace(" ", "").lower()
        for item in answer_list:
                item_processed = item.replace(" ", "").lower()
                if item_processed in generated_answer_processed:
                    find = 1
                    break
        write_to_file(output_path,f"generated answer: {generated_answer}")
        if find == 1:
            write_to_file(output_path,f"correct!")
            correct_num += 1
        else:
            write_to_file(output_path,f"wrong!")
            wrong_num += 1
    accuracy = (correct_num / (correct_num + wrong_num)) * 100
    write_to_file(output_path,f"{accuracy:.1f}%")