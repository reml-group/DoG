import os
from typing import Dict, List

import yaml
from bmtools.agent.singletool import import_all_apis, load_single_tools
from langchain.agents import Agent as langchainAgent

# from langchain.chat_models import ChatOpenAI
# from langchain.chat_models.base import BaseChatModel
# from langchain.llms import OpenAI
# from langchain.llms.base import BaseLLM
from agentverse.llms import OpenAICompletion, OpenAIChat, llm_registry

# from langchain.memory import ChatMessageHistory
from langchain.memory.prompt import _DEFAULT_SUMMARIZER_TEMPLATE
from langchain.prompts import PromptTemplate

# from agentverse.agents import Agent
from agentverse.agents import agent_registry
from agentverse.environments import BaseEnvironment, env_registry
from agentverse.memory import memory_registry
from agentverse.memory_manipulator import memory_manipulator_registry

# from agentverse.memory.memory import SummaryMemory
from agentverse.parser import output_parser_registry
import pdb

def load_llm(llm_config: Dict):
    llm_type = llm_config.pop("llm_type", "text-davinci-003")

    return llm_registry.build(llm_type, **llm_config)


def load_memory(memory_config: Dict):
    memory_type = memory_config.pop("memory_type", "chat_history")
    return memory_registry.build(memory_type, **memory_config)

def load_memory_manipulator(memory_manipulator_config: Dict):
    memory_manipulator_type = memory_manipulator_config.pop("memory_manipulator_type", "basic")
    return memory_manipulator_registry.build(memory_manipulator_type, **memory_manipulator_config)


def load_tools(tool_config: List[Dict]):
    if len(tool_config) == 0:
        return []
    all_tools_list = []
    for tool in tool_config:
        _, config = load_single_tools(tool["tool_name"], tool["tool_url"])
        all_tools_list += import_all_apis(config)
    return all_tools_list


def load_environment(env_config: Dict) -> BaseEnvironment:
    env_type = env_config.pop("env_type", "basic")
    return env_registry.build(env_type, **env_config)


def load_agent(agent_config: Dict) -> langchainAgent:
    agent_type = agent_config.pop("agent_type", "conversation")
    agent = agent_registry.build(agent_type, **agent_config)
    return agent


def prepare_task_config(task):
    """Read the yaml config of the given task in `tasks` directory."""
    all_task_dir = os.path.join(os.path.dirname(__file__), "tasks")
    task_path = os.path.join(all_task_dir, task)
    # pdb.set_trace()
    config_path = os.path.join(task_path, "config.yaml")
    if not os.path.exists(task_path):
        all_tasks = []
        for task in os.listdir(all_task_dir):
            if (
                os.path.isdir(os.path.join(all_task_dir, task))
                and task != "__pycache__"
            ):
                all_tasks.append(task)
                for subtask in os.listdir(os.path.join(all_task_dir, task)):
                    if (
                        os.path.isdir(os.path.join(all_task_dir, task, subtask))
                        and subtask != "__pycache__"
                    ):
                        all_tasks.append(f"{task}/{subtask}")
        raise ValueError(f"Task {task} not found. Available tasks: {all_tasks}")
    if not os.path.exists(config_path):
        raise ValueError(
            "You should include the config.yaml file in the task directory"
        )
    task_config = yaml.safe_load(open(config_path))

    # Build the output parser
    parser = output_parser_registry.build(task)
    task_config["output_parser"] = parser

    for i, agent_configs in enumerate(task_config["agents"]):
        agent_configs["memory"] = load_memory(agent_configs.get("memory", {}))
        memory_manipulator = load_memory_manipulator(agent_configs.get("memory_manipulator", {}))
        agent_configs["memory_manipulator"] = memory_manipulator
        if agent_configs.get("tool_memory", None) is not None:
            agent_configs["tool_memory"] = load_memory(agent_configs["tool_memory"])
        llm = load_llm(agent_configs.get("llm", "text-davinci-003"))
        agent_configs["llm"] = llm

        agent_configs["tools"] = load_tools(agent_configs.get("tools", []))

        agent_configs["output_parser"] = task_config["output_parser"]

    return task_config
