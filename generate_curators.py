# generate_catalog.py
import requests
import json
from src.curator import explain_object  # 너의 curator.py 파일 import

BASE = "https://collectionapi.metmuseum.org/public/collection/v1"

def search_met(query, limit=10):
    """키워드 검색 후 objectID 리스트 반환"""
    params = {
        "q": query,
        "hasImages": "true",
        "title": "true",
        "tags": "true"
    }
    resp = requests.get(f"{BASE}/search", params=params)
    data = resp.json()
    object_ids = data.get("objectIDs", [])
    return object_ids[:limit]  # 최대 limit개만 사용

def fetch_object_metadata(object_id):
    """objectID로 상세 메타데이터 가져오기"""
    resp = requests.get(f"{BASE}/objects/{object_id}")
    return resp.json()

def generate_catalog(query, output_file="generated_catalog.json"):
    """검색 → curator note 생성 → JSON 파일 저장"""
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

    # generated_catalog.json에 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"Catalog saved to {output_file}")

# 사용 예
if __name__ == "__main__":
    generate_catalog("sunflowers", output_file="generated_catalog.json")
