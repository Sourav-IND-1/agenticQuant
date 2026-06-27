"""
backend/database/supabase_client.py

Initializes Supabase connection using credentials from environment (.env).
Exposes module-level 'client' variable. Includes robust in-memory fallback
table storage if network connection or SSL verification fails.
"""

import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import backend.config as config

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None


class InMemoryTable:
    def __init__(self, table_name: str, store: dict):
        self.table_name = table_name
        self.store = store
        if table_name not in self.store:
            self.store[table_name] = []
        self._current_query = list(self.store[table_name])

    def insert(self, record):
        if isinstance(record, dict):
            self.store[self.table_name].insert(0, record)
            self._current_query = [record]
        elif isinstance(record, list):
            for r in record:
                self.store[self.table_name].insert(0, r)
            self._current_query = record
        return self

    def update(self, record):
        # Applied to items matching filter
        for item in self._current_query:
            item.update(record)
        return self

    def select(self, *args, **kwargs):
        self._current_query = list(self.store[self.table_name])
        return self

    def eq(self, field: str, value):
        self._current_query = [item for item in self._current_query if item.get(field) == value]
        return self

    def order(self, field: str, desc: bool = False):
        try:
            self._current_query.sort(key=lambda x: str(x.get(field, "")), reverse=desc)
        except Exception:
            pass
        return self

    def limit(self, n: int):
        self._current_query = self._current_query[:n]
        return self

    def execute(self):
        class Response:
            def __init__(self, data):
                self.data = data
        return Response(self._current_query)


class InMemorySupabaseClient:
    """Fallback in-memory database client mimicking supabase-py API."""
    def __init__(self):
        self.store = {}

    def table(self, name: str) -> InMemoryTable:
        return InMemoryTable(name, self.store)


def _init_client():
    url = config.SUPABASE_URL or os.getenv("SUPABASE_URL", "")
    key = config.SUPABASE_KEY or os.getenv("SUPABASE_KEY", "")

    if url and key and create_client is not None:
        try:
            return create_client(url, key)
        except Exception as e:
            print(f"[supabase_client] Supabase live connection failed ({e}). Using in-memory fallback.")
    return InMemorySupabaseClient()


# Module-level client variable
client = _init_client()


def get_supabase_client():
    """Returns the module-level client (live Supabase or InMemoryFallback)."""
    global client
    return client


if __name__ == "__main__":
    c = get_supabase_client()
    print("Initialized Supabase Client Type:", type(c).__name__)
