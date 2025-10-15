from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from .extractor import extract_text_from_url
from .gemini_client import analyze_with_gemini
from .models import AnalysisRequest, AnalysisResult
@app.get("/healthz")
def health():
    return {"status": "ok"}


app = FastAPI(title="Fake News Detector API")

@app.post("/analyze", response_model=AnalysisResult)
async def analyze(req: AnalysisRequest):
    text = req.text
    if req.url and not text:
        text = await extract_text_from_url(req.url)
        if not text:
            raise HTTPException(status_code=400, detail="Couldn't extract article text from URL")
    if not text or len(text) < 50:
        raise HTTPException(status_code=400, detail="Please provide article text or a valid URL with sufficient content.")

    gemini_resp = await analyze_with_gemini(text, url=req.url)

    # Combine heuristics + gemini response could be added here. For simplicity return the analyzer result.
    return AnalysisResult(
        label=gemini_resp.get("label", "unknown"),
        confidence=float(gemini_resp.get("confidence", 0.0)),
        summary=gemini_resp.get("summary", ""),
        explanation=gemini_resp.get("explanation", []),
        highlights=gemini_resp.get("highlights", []),
        raw=gemini_resp,
    )


