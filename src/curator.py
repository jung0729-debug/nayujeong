# src/curator.py
import os
from functools import lru_cache
import groq  # groq SDK import

GROQ_KEY = os.getenv("GROQ_API_KEY")
client = groq.Client(api_key=GROQ_KEY) if GROQ_KEY else None

SYSTEM_PROMPT = (
    "You are a professional museum curator. Your tone is polished, evocative, and authoritative yet accessible."
)

USER_TEMPLATE = (
    "Write a 150-220 word curator note about the following artwork. "
    "Include: (1) brief context, (2) visual analysis, (3) interpretive insight, (4) a viewing tip.\n"
    "Metadata: {meta}\n"
)

def _meta_to_str(meta):
    fields = ["title", "artistDisplayName", "objectDate", "medium", "dimensions", "creditLine"]
    parts = []
    for k in fields:
        v = meta.get(k)
        if v:
            parts.append(f"{k}: {v}")
    if meta.get("objectID"):
        parts.append(f"objectID: {meta.get('objectID')}")
    return "; ".join(parts)

@lru_cache(maxsize=256)
def _call_groq_for_object(object_id, meta_str):
    """Internal cached call by object id using Groq API."""
    if not client:
        return None
    try:
        response = client.completions.create(
            model="groq-museum-curator",  # 예시 모델명
            prompt=f"{SYSTEM_PROMPT}\n{USER_TEMPLATE.format(meta=meta_str)}",
            max_tokens=400,
            temperature=0.3
        )
        # Groq SDK에 따라 response 구조 조정 필요
        return response.choices[0].text
    except Exception as e:
        return f"Groq request failed: {e}"

def explain_object(meta):
    """
    Given a MET metadata dict, return a curator note.
    If Groq key missing, return a helpful placeholder.
    """
    if not meta:
        return "No metadata provided."
    object_id = meta.get("objectID")
    meta_str = _meta_to_str(meta)
    if not client:
        title = meta.get("title", "Untitled")
        artist = meta.get("artistDisplayName", "Unknown Artist")
        date = meta.get("objectDate", "")
        return f"{title} — {artist} ({date}). [Groq API key not set: set GROQ_API_KEY to generate a full curator note.]"

    result = _call_groq_for_object(object_id, meta_str)
    if result is None:
        return "Groq client not configured correctly."
    return result
