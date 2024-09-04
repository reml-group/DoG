from typing import Dict
from agentverse.registry import Registry

env_registry = Registry(name="EnvironmentRegistry")

from .base import BaseEnvironment
from .basic import BasicEnvironment
from .llm_eval import LLMEvalEnvironment
