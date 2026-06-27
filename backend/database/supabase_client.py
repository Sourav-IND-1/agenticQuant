from typing import Optional, Any
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

def get_supabase_client() -> Optional[Any]:
    """Initializes and returns the Supabase client using credentials from environment."""
    if not config.SUPABASE_URL or not config.SUPABASE_KEY or create_client is None:
        return None
    try:
        return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    except Exception as e:
        print(f"Warning initializing Supabase client: {e}")
        return None

if __name__ == "__main__":
    client = get_supabase_client()
    if client:
        print("Supabase client initialized successfully with URL:", config.SUPABASE_URL)
    else:
        print("Supabase client running in offline cache mode.")
