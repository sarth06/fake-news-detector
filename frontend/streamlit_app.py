import streamlit as st
import requests
import os
from urllib.parse import urljoin

API_URL = os.getenv("https://fake-news-detector-vfeq.onrender.com")

st.set_page_config(page_title="Fake News Detector — Student", layout="wide")
st.title("📰 Fake News Detector — Student Edition")

with st.form("analyze_form"):
    url = st.text_input("Article URL (optional)")
    text = st.text_area("Or paste article text (recommended for short pieces)", height=250)
    submitted = st.form_submit_button("Analyze")

if submitted:
    payload = {"url": url or None, "text": text or None}
    with st.spinner("Analyzing..."):
        try:
            resp = requests.post(API_URL, json=payload, timeout=60)
        except Exception as e:
            st.error(f"Could not reach backend API: {e}")
            st.stop()
    if resp.status_code != 200:
        st.error(f"Error from API: {resp.status_code} — {resp.text}")
    else:
        data = resp.json()
        st.subheader(f"Verdict: {data.get('label', 'unknown').upper()} — confidence {data.get('confidence')}")
        st.markdown("**Summary**")
        st.write(data.get('summary'))
        st.markdown("**Why this verdict?**")
        for b in data.get('explanation', []):
            st.write(f"- {b}")

        st.markdown("**Flagged sentences / claims**")
        for h in data.get('highlights', []):
            st.info(f"{h.get('sentence')}\n\nReason: {h.get('reason')}\nClaim: {h.get('claim')}")

        st.markdown("---")
        st.caption("Tip: When in doubt, cross-check with multiple trusted outlets and look for original sources or official statements.")
