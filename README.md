# Fake News Detector — Student Edition (Final Submission)

This is a complete, ready-to-run student project that includes:
- FastAPI backend (`/backend`) which analyzes article text and returns a credibility verdict.
- Streamlit frontend (`/frontend`) for students to paste a URL or text and get a verdict.
- A **free fallback analyzer** so the project works without any paid LLM or API key.
- Optional Gemini integration: if you supply `GEMINI_API_KEY` and `GEMINI_API_URL` the backend will use it.

## Quick start (local)

1. Make sure you have Python 3.11+ and `pip` installed.
2. (Optional but recommended) create and activate a virtualenv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # mac/linux
   .\.venv\Scripts\activate # windows (powershell)
   ```
3. Install dependencies (backend and frontend share requirements):
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Start the backend (from repo root):
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```
5. In another terminal, run the Streamlit frontend:
   ```bash
   cd frontend
   streamlit run streamlit_app.py
   ```
6. Open the Streamlit UI printed in your terminal (usually http://localhost:8501).

## Gemini integration (optional)
- If you have a Gemini-compatible API, set these environment variables in `.env` or your shell before starting the backend:
  ```bash
  GEMINI_API_KEY=your_key_here
  GEMINI_API_URL=https://api.your-gemini-endpoint.example/generate
  ```
- If `GEMINI_API_KEY` is not set, the backend will run a free heuristic analyzer (no network calls).

## Files included
- backend/app/*.py (FastAPI application)
- backend/requirements.txt
- backend/Dockerfile
- frontend/streamlit_app.py
- docker-compose.yml

## What I couldn't do
- I didn't include actual paid Gemini call code tied to a specific cloud provider by default. Instead, the code includes a safe optional adapter and a deterministic free analyzer so your submission runs without any paid service.

## Next steps (if you want me to do more)
- I can adapt the Gemini client to a specific Gemini API (Google Cloud Generative API) if you provide which one to target.
- I can also build a small test suite or GitHub Actions workflow to run linting/tests.

Good luck with your submission — this is ready to run locally and to zip/upload as your final project!\n