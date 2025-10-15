import os, json, asyncio, re
from typing import List, Dict
import httpx

# Prefer GOOGLE_API_KEY for Google Cloud Generative API; fall back to GEMINI_API_KEY for compat.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
# Model selection (tweak via env)
GEMINI_MODEL = os.getenv("GEMINI_MODEL") or "gemini-1.5-mini"
GENERATIVE_ENDPOINT = os.getenv("GENERATIVE_ENDPOINT") or f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

async def analyze_with_gemini(text: str, url: str | None = None) -> dict:
    """If GOOGLE_API_KEY (or GEMINI_API_KEY) is set, call Google Generative API's generateContent.
    Otherwise fall back to the local deterministic analyzer.

    NOTE: Google sometimes changes model names / availability. If you get a 404, try a different GEMINI_MODEL like
    'gemini-1.5-flash' or 'gemini-2.5-flash' and set GOOGLE_API_KEY accordingly.
    """
    if GOOGLE_API_KEY:
        try:
            payload = _build_generatecontent_payload(text, url)
            params = {"key": GOOGLE_API_KEY}
            headers = {"Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(GENERATIVE_ENDPOINT, params=params, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            # The Google generateContent response usually contains 'candidates' or 'output' fields.
            # Try to extract text from typical fields; else return the whole response.
            # Look for 'candidates' -> list of objects with 'content' or 'output' keys.
            text_out = None
            if isinstance(data, dict):
                # nested search for first textual candidate
                if 'candidates' in data and isinstance(data['candidates'], list) and data['candidates']:
                    cand = data['candidates'][0]
                    # candidate might be dict with 'content' or 'output' or 'text'
                    if isinstance(cand, dict):
                        text_out = cand.get('content') or cand.get('text') or cand.get('output')
                # some endpoints return 'output' as dict
                if text_out is None and 'output' in data:
                    out = data['output']
                    if isinstance(out, dict):
                        text_out = out.get('content') or out.get('text')
            if not text_out:
                # fallback: try to stringify some reasonable portion
                text_out = json.dumps(data)
            # attempt parse JSON from assistant if it returned structured JSON
            try:
                parsed = json.loads(text_out)
                return parsed
            except Exception:
                # interpret text_out as plain assistant message: we will wrap it
                return {
                    "label": "unknown",
                    "confidence": 0.0,
                    "summary": text_out[:1000],
                    "explanation": ["LLM returned unstructured text; see raw for details."],
                    "highlights": [],
                    "raw_response": data,
                }
        except Exception as e:
            # If remote call fails, log into raw and fallback
            return {"label":"unknown","confidence":0.0,"summary":"Google Generative API call failed; falling back to local analyzer.","explanation":[str(e)],"highlights":[]}
    # No API key: use local analyzer
    return _local_analyzer(text, url)

def _build_generatecontent_payload(text: str, url: str | None) -> dict:
    # Build a simple generateContent payload using 'contents' with a text part.
    prompt = _compose_prompt(text, url)
    return {
        "contents": [
            {
                "role": "user",
                "parts": [{"type": "input_text", "text": prompt}]
            }
        ],
        "temperature": 0.0,
        "maxOutputTokens": 800
    }

def _compose_prompt(text: str, url: str | None) -> str:
    return f"You are a helpful fact-check assistant for students. Analyze the article and return a JSON object with fields: label (credible|mixed|fake), confidence (0.0-1.0), summary (1-3 sentences), explanation (list of 3 bullets), highlights (list up to 5 {{sentence, reason, claim}}).\n\nArticleURL: {url}\n\nArticleText:\n{text[:15000]}"

def _simple_summary(text: str, max_sent=3) -> str:
    import re
    sents = re.split(r'(?<=[.!?])\\s+', text.strip())
    sents = [s.strip() for s in sents if s.strip()]
    return ' '.join(sents[:max_sent]) if sents else (text[:300] + '...')

def _local_analyzer(text: str, url: str | None) -> dict:
    import re
    lowered = text.lower()
    sensational_words = ["shocking","unbelievable","miracle","exposed","secret","you won't believe","breakthrough"]
    score = 0.5
    reasons = []

    sensational_count = sum(lowered.count(w) for w in sensational_words)
    if sensational_count:
        score -= min(0.25, 0.05 * sensational_count)
        reasons.append(f"Found sensational language ({sensational_count} match(es)).")

    links = len(re.findall(r'https?://', text))
    if links >= 2:
        score += 0.15
        reasons.append(f"Contains {links} external links (potential sources).")

    numbers = len(re.findall(r'\\b\\d{2,}\\b', text))
    if numbers and links == 0:
        score -= 0.15
        reasons.append("Contains numeric claims but no obvious citations or links.")

    if len(text) < 300:
        score -= 0.1
        reasons.append("Article is very short; may lack context.")

    score = max(0.0, min(1.0, score))

    if score >= 0.7:
        label = 'credible'
    elif score >= 0.4:
        label = 'mixed'
    else:
        label = 'fake'

    sents = re.split(r'(?<=[.!?])\\s+', text.strip())
    highlights = []
    for s in sents:
        if len(highlights) >= 5:
            break
        if re.search(r'\\b\\d{2,}\\b', s) or re.search(r'\\b(?:always|never|proves|confirm|disproves)\\b', s.lower()):
            highlights.append({"sentence": s.strip(), "reason": "Contains numeric/strong claim", "claim": s.strip()})
    if not highlights and sents:
        highlights.append({"sentence": sents[0].strip(), "reason": "Lead sentence", "claim": sents[0].strip()})

    return {
        "label": label,
        "confidence": round(score, 2),
        "summary": _simple_summary(text, max_sent=3),
        "explanation": reasons or ["No strong signals found; treat with caution."],
        "highlights": highlights,
    }
