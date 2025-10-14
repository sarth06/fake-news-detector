# Fake News Detector — Student Edition

## Overview
The Fake News Detector is a lightweight web application intended for students to rapidly assess the credibility
of online articles. It combines simple explainable heuristics with an optional Large Language Model (Gemini) adapter
so the tool works both offline (free) and with Google Cloud's Generative API for richer analysis.

## Objectives
- Provide an easy-to-run submission suitable for coursework.
- Offer transparent, explainable signals students can understand (sensational language, presence of links, numeric claims).
- Allow optional use of Google's Gemini models for stronger natural-language summaries and structured outputs.

## Architecture
- **Frontend**: Streamlit app (`frontend/streamlit_app.py`) where users paste a URL or raw text.
- **Backend**: FastAPI (`backend/app`) exposing `/analyze` which returns a JSON result including label, confidence,
  concise summary, explanation bullets, and highlighted sentences.
- **LLM Adapter**: `backend/app/gemini_client.py` — calls Google Generative API when `GOOGLE_API_KEY` (or `GEMINI_API_KEY`) is provided.
  If no key is present, a deterministic `_local_analyzer` runs so the app remains fully functional offline.

## How it works (high-level)
1. User supplies a URL or article text.
2. Backend extracts text (if URL) and runs lightweight heuristics.
3. If an API key is present, the backend also asks the Gemini model to produce a structured JSON-like analysis.
4. The frontend shows: verdict (credible/mixed/fake), confidence score, short summary, explanation bullets, and flagged claims.

## Security & Ethics
- API keys must never be committed. Use environment variables or a secrets manager in production.
- The LLM output may hallucinate — students should verify important claims via original sources.
- Fetching arbitrary URLs can be risky; the demo uses timeouts and a safe extraction function, but a production build
  should add an allowlist and additional sanitization.

## Running the project
See `README.md` at project root for quick start instructions. The app runs locally without any paid services.

## Evaluation examples (included in demo script)
- Credible: a linked journalism piece quoting named sources.
- Mixed: opinion pieces with some numbers but limited sourcing.
- Fake-style: short sensational article with no links and many strong claims.

## Conclusion
This project is submission-ready and includes both the implementation and documentation needed for evaluation.
