# src/met_api.py
import requests
from functools import lru_cache

BASE = "https://collectionapi.metmuseum.org/public/collection/v1"

def search(q, hasImages=True, max_results=50):
    """Search The Met collection."""
    try:
        r = requests.get(f"{BASE}/search", params={"q": q, "hasImages": hasImages})
        r.raise_for_status()
        data = r.json()
        ids = data.get("objectIDs") or []
        return ids[:max_results]
    except Exception:
        return []

@lru_cache(maxsize=1024)
def get_object(object_id):
    """Get full object metadata by id."""
    try:
        r = requests.get(f"{BASE}/objects/{object_id}")
        r.raise_for_status()
        return r.json()
    except Exception:
        return {"objectID": object_id, "title": "(failed to fetch)", "primaryImageSmall": None}
