# import streamlit as st
# import requests
# import os
# from urllib.parse import urljoin

# API_URL = os.getenv("FND_API_URL", "http://localhost:8000/analyze")

# st.set_page_config(page_title="Fake News Detector — Student", layout="wide")
# st.title("📰 Fake News Detector — Student Edition")

# with st.form("analyze_form"):
#     url = st.text_input("Article URL (optional)")
#     text = st.text_area("Or paste article text (recommended for short pieces)", height=250)
#     submitted = st.form_submit_button("Analyze")

# if submitted:
#     payload = {"url": url or None, "text": text or None}
#     with st.spinner("Analyzing..."):
#         try:
#             resp = requests.post(API_URL, json=payload, timeout=60)
#         except Exception as e:
#             st.error(f"Could not reach backend API: {e}")
#             st.stop()
#     if resp.status_code != 200:
#         st.error(f"Error from API: {resp.status_code} — {resp.text}")
#     else:
#         data = resp.json()
#         st.subheader(f"Verdict: {data.get('label', 'unknown').upper()} — confidence {data.get('confidence')}")
#         st.markdown("**Summary**")
#         st.write(data.get('summary'))
#         st.markdown("**Why this verdict?**")
#         for b in data.get('explanation', []):
#             st.write(f"- {b}")

#         st.markdown("**Flagged sentences / claims**")
#         for h in data.get('highlights', []):
#             st.info(f"{h.get('sentence')}\n\nReason: {h.get('reason')}\nClaim: {h.get('claim')}")

#         st.markdown("---")
#         st.caption("Tip: When in doubt, cross-check with multiple trusted outlets and look for original sources or official statements.")
# frontend/streamlit_app.py
import os
import sys
import asyncio
import streamlit as st

# Ensure repo root is on Python path so we can import backend package
# (frontend/ is inside repo root; go up one level)
THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Now import the functions from your backend package
# Adjust module path if your backend structure is different
try:
    from backend.app.extractor import extract_text_from_url
    from backend.app.gemini_client import analyze_with_gemini
except Exception as e:
    st.error("Failed to import backend functions. See console for details.")
    raise

st.set_page_config(page_title="Fake News Detector", layout="wide")

st.title("📰 Fake News Detector")

col1, col2 = st.columns([3, 1])

with col1:
    url_input = st.text_input("Enter article URL (optional):")
    text_input = st.text_area("Or paste the article text here:", height=300)

with col2:
    st.write("Options")
    # put any other UI controls here (model choice, etc.)
    analyze_btn = st.button("Analyze")

def run_extract_text(url: str) -> str:
    """
    Calls the backend extractor. The backend extractor is async,
    so we use asyncio.run to execute it synchronously here.
    """
    return asyncio.run(extract_text_from_url(url))

def run_gemini_analysis(text: str, url: str | None = None) -> dict:
    """
    Calls the backend Gemini analyzer (async).
    """
    return asyncio.run(analyze_with_gemini(text, url=url))

if analyze_btn:
    if not text_input.strip() and not url_input.strip():
        st.warning("Please provide article text or a URL.")
    else:
        with st.spinner("Analyzing..."):
            try:
                # If URL is provided but text is empty, extract text
                if url_input.strip() and not text_input.strip():
                    extracted = run_extract_text(url_input.strip())
                    if not extracted:
                        st.error("Couldn't extract article text from the URL. Try a different URL or paste the text manually.")
                        st.stop()
                    text_input = extracted

                # Run the analysis
                gemini_resp = run_gemini_analysis(text_input, url=url_input.strip() or None)

                # Present results
                label = gemini_resp.get("label", "unknown")
                confidence = float(gemini_resp.get("confidence", 0.0))
                summary = gemini_resp.get("summary", "")
                explanation = gemini_resp.get("explanation", [])
                highlights = gemini_resp.get("highlights", [])

                st.markdown("## Result")
                st.write(f"**Label:** {label}")
                st.write(f"**Confidence:** {confidence:.2f}")

                if summary:
                    st.markdown("### Summary")
                    st.write(summary)

                if explanation:
                    st.markdown("### Explanation")
                    for i, e in enumerate(explanation, 1):
                        st.write(f"{i}. {e}")

                if highlights:
                    st.markdown("### Highlights")
                    for h in highlights:
                        st.write(f"- {h}")

                # Optional: show raw response for debugging
                with st.expander("Raw response (debug)"):
                    st.json(gemini_resp)

            except Exception as exc:
                st.error(f"An error occurred during analysis: {exc}")
                raise
