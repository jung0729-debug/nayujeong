
import os
from functools import lru_cache
from openai import OpenAI

# 네 API 키를 여기 넣으면 됩니다
OPENAI_KEY = "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"
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

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
    parts = [f"{k}: {meta[k]}" for k in fields if meta.get(k)]
    if meta.get("objectID"):
        parts.append(f"objectID: {meta['objectID']}")
    return "; ".join(parts)

@lru_cache(maxsize=256)
def _call_openai_for_object(object_id, meta_str):
    if not client:
        return None
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_TEMPLATE.format(meta=meta_str)}
            ],
            temperature=0.3,
            max_tokens=400
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"OpenAI request failed: {e}"

def explain_object(meta):
    if not meta:
        return "No metadata provided."
    object_id = meta.get("objectID")
    meta_str = _meta_to_str(meta)
    if not client:
        title = meta.get("title", "Untitled")
        artist = meta.get("artistDisplayName", "Unknown Artist")
        date = meta.get("objectDate", "")
        return f"{title} — {artist} ({date}). [OpenAI API key not set: set OPENAI_API_KEY to generate a full curator note.]"

    result = _call_openai_for_object(object_id, meta_str)
    if result is None:
        return "OpenAI client not configured correctly."
    return result
