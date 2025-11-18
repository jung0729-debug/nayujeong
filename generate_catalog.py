import requests
import json
from src.curator import explain_object

BASE = "https://collectionapi.metmuseum.org/public/collection/v1"

def search_met(query, limit=10):
    params = {"q": query, "hasImages": "true", "title": "true", "tags": "true"}
    resp = requests.get(f"{BASE}/search", params=params)
    data = resp.json()
    object_ids = data.get("objectIDs", [])
    return object_ids[:limit]

def fetch_object_metadata(object_id):
    resp = requests.get(f"{BASE}/objects/{object_id}")
    return resp.json()

def generate_catalog(query, output_file="generated_catalog.json"):
    catalog = []
    object_ids = search_met(query)
    if not object_ids:
        print("검색 결과 없음")
    for oid in object_ids:
        meta = fetch_object_metadata(oid)
        note = explain_object(meta)
        entry = {
            "objectID": oid,
            "title": meta.get("title"),
            "artist": meta.get("artistDisplayName"),
            "objectDate": meta.get("objectDate"),
            "image": meta.get("primaryImage"),
            "curator_note": note
        }
        catalog.append(entry)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"Catalog saved to {output_file}")

if __name__ == "__main__":
    generate_catalog("sunflowers")
