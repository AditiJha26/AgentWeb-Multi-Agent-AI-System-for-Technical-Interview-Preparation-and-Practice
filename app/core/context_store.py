# app/core/context_store.py

class ContextStore:
    def __init__(self):
        self.store = {}

    def set(self, key, value):
        self.store[key] = value

    def get(self, key, default=None):
        return self.store.get(key, default)

    def get_all(self):
        return self.store

    def update(self, key, func):
        current = self.store.get(key)
        self.store[key] = func(current)
