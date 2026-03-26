"""
Atomic Vision - Gemini Vision AI Backend
Uses Google Gemini 1.5 Flash to directly analyze book page images.
OCR is used only for raw text display; all smart analysis is done by Gemini.
"""

import os
import re
import json
from dotenv import load_dotenv

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import pytesseract
from google import genai
from google.genai import types as genai_types
from PIL import Image
import io

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================================================
# CONFIG
# ============================================================================
DEBUG = False
TEMP_DIR = Path("/tmp")
try:
    TEMP_DIR.mkdir(exist_ok=True)
except Exception:
    pass

# Gemini API Key (loaded from .env file)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Failed to init Gemini Client: {e}")

GEMINI_MODEL = "gemini-2.5-flash"

# Tesseract (for raw OCR text display only)
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
]
TESSERACT_FOUND = False
for path in TESSERACT_PATHS:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        TESSERACT_FOUND = True
        break

if not TESSERACT_FOUND:
    import shutil
    if shutil.which("tesseract"):
        TESSERACT_FOUND = True

# ============================================================================
# PYDANTIC MODELS
# ============================================================================
class ConfidenceScore(BaseModel):
    value: Optional[str]
    confidence: float

class DifficultWord(BaseModel):
    word: str
    meaning: str
    difficulty_score: float

class PageAnalysisResponse(BaseModel):
    raw_ocr_text: str
    ocr_confidence: float
    title: ConfidenceScore
    author: ConfidenceScore
    best_quote: str
    quote_confidence: float
    summary: list[str]
    summary_confidence: float
    context_explanation: str
    context_confidence: float
    difficult_words: list[DifficultWord]
    has_sufficient_info: bool
    message: str

# ============================================================================
# IMAGE PREPROCESSING (for clean Gemini input)
# ============================================================================
def preprocess_image(img_bytes: bytes) -> np.ndarray:
    image_array = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Upscale for better quality
    h, w = gray.shape
    if h < 1500 or w < 1500:
        scale = max(1500.0 / h, 1500.0 / w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Unsharp masking to sharpen text
    gaussian = cv2.GaussianBlur(gray, (0, 0), 2.0)
    sharpened = cv2.addWeighted(gray, 1.5, gaussian, -0.5, 0)

    _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if DEBUG:
        cv2.imwrite(str(TEMP_DIR / "debug_preprocessed.png"), binary)

    return binary

def get_raw_ocr(preprocessed: np.ndarray) -> dict:
    """Get raw OCR text for display only."""
    if not TESSERACT_FOUND:
        return {"text": "(Tesseract not installed — raw text unavailable)", "confidence": 0.0}
    try:
        text = pytesseract.image_to_string(preprocessed, lang="eng", config="--psm 3")
        data = pytesseract.image_to_data(
            preprocessed, lang="eng", config="--psm 3", output_type=pytesseract.Output.DICT
        )
        confidences = [int(c) / 100.0 for c in data["conf"] if c != '-1' and int(c) > 0]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        # Clean up raw text
        text = re.sub(r'-\n\s*', '', text)
        text = re.sub(r'\n+', ' ', text).strip()

        return {"text": text, "confidence": round(avg_conf, 2)}
    except Exception as e:
        print(f"OCR error: {e}")
        return {"text": "", "confidence": 0.0}

# ============================================================================
# GEMINI VISION ANALYSIS
# ============================================================================
GEMINI_PROMPT = """You are an expert book analyst. Carefully look at this book page image and extract the following information. 

Return ONLY a valid JSON object with this exact structure (no markdown, no explanation, just JSON):

{
  "title": "The exact book title if visible or inferable from context, else null",
  "author": "The author's full name if mentioned anywhere on the page, else null",
  "best_quote": "The single most insightful, meaningful or memorable sentence from this page",
  "summary": [
    "First key point from this page",
    "Second key point from this page", 
    "Third key point from this page"
  ],
  "difficult_words": [
    {"word": "Word1", "meaning": "Clear definition", "difficulty_score": 0.8},
    {"word": "Word2", "meaning": "Clear definition", "difficulty_score": 0.6}
  ],
  "context_explanation": "A 1-2 sentence explanation of what this page is about and its significance in the broader context",
  "confidence": 0.95
}

Rules:
- For title/author: ONLY provide if you are confident. Set to null if not sure.
- For summary: Give exactly 3 distinct key points as separate list items.
- For difficult_words: List up to 4 advanced vocabulary words from this page with accurate definitions and a difficulty_score from 0.0 to 1.0
- For best_quote: Pick the most quotable, meaningful sentence verbatim from the page.
- confidence: Your overall confidence in the analysis from 0.0 to 1.0
"""

def analyze_with_gemini(img_bytes: bytes) -> dict:
    """Send image directly to Gemini Vision and get structured analysis."""
    if not client:
        raise HTTPException(status_code=500, detail="Gemini API Key is missing. Please set GEMINI_API_KEY in Vercel Environment Variables.")
    raw_response = "(no response received)"
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                genai_types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                GEMINI_PROMPT,
            ],
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )

        raw_response = response.text.strip()
        if DEBUG:
            with open(TEMP_DIR / "debug_gemini_response.txt", "w", encoding="utf-8") as f:
                f.write(raw_response)

        # Strip markdown code fences if present
        if raw_response.startswith("```"):
            raw_response = re.sub(r'^```(?:json)?\s*', '', raw_response)
            raw_response = re.sub(r'\s*```$', '', raw_response)

        return json.loads(raw_response)

    except json.JSONDecodeError as e:
        print(f"Gemini JSON parse error: {e}\nRaw: {raw_response}")
        raise Exception(f"Gemini returned invalid JSON: {e}")
    except Exception as e:
        print(f"Gemini API error: {e}")
        raise

# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(title="Atomic Vision — Gemini Vision API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/ping")
async def ping():
    return {"status": "ok", "engine": "gemini-2.5-flash", "tesseract": TESSERACT_FOUND}

@app.post("/analyze-page", response_model=PageAnalysisResponse)
async def analyze_page(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()

        # 1. Preprocess for OCR raw text display
        preprocessed = preprocess_image(img_bytes)
        ocr_result = get_raw_ocr(preprocessed)

        # 2. Gemini Vision — the real analysis engine
        gemini_data = analyze_with_gemini(img_bytes)

        # 3. Parse Gemini response
        title_val   = gemini_data.get("title")
        author_val  = gemini_data.get("author")
        best_quote  = gemini_data.get("best_quote", "")
        summary     = gemini_data.get("summary", [])
        context     = gemini_data.get("context_explanation", "")
        confidence  = float(gemini_data.get("confidence", 0.9))

        # Build difficult words list
        raw_words = gemini_data.get("difficult_words", [])
        difficult_words = [
            DifficultWord(
                word=w.get("word", ""),
                meaning=w.get("meaning", ""),
                difficulty_score=float(w.get("difficulty_score", 0.5))
            )
            for w in raw_words if w.get("word")
        ]

        # Ensure summary is a list of strings
        if isinstance(summary, str):
            summary = [summary]

        return PageAnalysisResponse(
            raw_ocr_text=ocr_result["text"],
            ocr_confidence=ocr_result["confidence"],
            title=ConfidenceScore(value=title_val, confidence=0.99 if title_val else 0.0),
            author=ConfidenceScore(value=author_val, confidence=0.99 if author_val else 0.0),
            best_quote=best_quote,
            quote_confidence=confidence,
            summary=summary,
            summary_confidence=confidence,
            context_explanation=context,
            context_confidence=confidence,
            difficult_words=difficult_words,
            has_sufficient_info=True,
            message="Analyzed by Gemini 2.5 Flash Vision AI ✨"
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
