

# app/core/mcp.py

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name, context):
        self.name = name
        self.context = context  # ContextStore instance

    @abstractmethod
    def run(self, input_data):
        pass

    def update_context(self, key, value):
        self.context.set(key, value)

    def get_context(self, key, default=None):
        return self.context.get(key, default)
