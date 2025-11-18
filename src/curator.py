# src/curator.py
import os
from functools import lru_cache
from openai import OpenAI

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = None
if OPENAI_KEY:
    client = OpenAI(api_key=OPENAI_KEY)

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
    # include objectID
    if meta.get("objectID"):
        parts.append(f"objectID: {meta.get('objectID')}")
    return "; ".join(parts)

@lru_cache(maxsize=256)
def _call_openai_for_object(object_id, meta_str):
    """Internal cached call by object id."""
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
        # Depending on OpenAI SDK, structure may differ; this expects .choices[0].message.content
        return res.choices[0].message.content
    except Exception as e:
        return f"LLM request failed: {e}"

def explain_object(meta):
    """
    Given a MET metadata dict, return a curator note.
    If OpenAI key missing, return a helpful placeholder.
    """
    if not meta:
        return "No metadata provided."
    object_id = meta.get("objectID")
    meta_str = _meta_to_str(meta)
    if not client:
        # placeholder fallback with helpful hint
        title = meta.get("title", "Untitled")
        artist = meta.get("artistDisplayName", "Unknown Artist")
        date = meta.get("objectDate", "")
        return f"{title} — {artist} ({date}). [OpenAI API key not set: set OPENAI_API_KEY to generate a full curator note.]"

    # call cached wrapper
    result = _call_openai_for_object(object_id, meta_str)
    if result is None:
        return "OpenAI client not configured correctly."
    return result
