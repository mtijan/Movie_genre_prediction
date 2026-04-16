"""
Movie Genre Prediction API
FastAPI application untuk memprediksi genre film dari sinopsis/overview.
"""

import sys
from pathlib import Path

# tambahkan root project ke sys.path agar bisa import src.predict
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.schemas import HealthResponse, InfoResponse, PredictRequest, PredictResponse
from src.predict import get_supported_genres, is_model_loaded, predict

# ──────────────────────────────────────────
# App Setup
# ──────────────────────────────────────────

app = FastAPI(
    title="🎬 Movie Genre Prediction API",
    description=(
        "API untuk memprediksi genre film berdasarkan sinopsis (overview). "
        "Model menggunakan TF-IDF + LinearSVC yang dilatih dengan dataset TMDB."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — izinkan semua origin (ubah untuk production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────
# Startup Event — pre-load model
# ──────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Load model saat API pertama kali dijalankan."""
    try:
        from src.predict import load_model
        load_model()
        print("[startup] Model berhasil di-load.")
    except FileNotFoundError as e:
        print(f"[startup] WARNING: {e}")
        print("[startup] Jalankan training terlebih dahulu: python src/train.py")


# ──────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────

@app.get("/", tags=["UI"])
def root():
    """Halaman Utama antarmuka AI (Web UI)."""
    ui_path = Path(__file__).parent / "index.html"
    if ui_path.exists():
        return FileResponse(ui_path)
    return {"error": "UI file (index.html) not found"}


@app.get("/health", response_model=HealthResponse, tags=["Info"])
def health():
    """Cek status API dan apakah model sudah ter-load."""
    try:
        genres = get_supported_genres()
        return HealthResponse(
            status="ok",
            model_loaded=True,
            supported_genres=genres,
        )
    except Exception:
        return HealthResponse(
            status="degraded",
            model_loaded=False,
            supported_genres=[],
        )


@app.get("/genres", tags=["Info"])
def genres():
    """Mengembalikan daftar genre yang bisa diprediksi oleh model."""
    try:
        return {"genres": get_supported_genres()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
def predict_genre(request: PredictRequest):
    """
    Prediksi genre film dari teks sinopsis (overview).

    - **overview**: Teks deskripsi/sinopsis film dalam bahasa Inggris (min 10 karakter)

    Returns genre yang diprediksi beserta confidence score.
    """
    try:
        result = predict(request.overview)
        return PredictResponse(
            genre=result["genre"],
            confidence=result["confidence"],
            all_scores=result["all_scores"],
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Model belum tersedia. Jalankan training terlebih dahulu. Detail: {e}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")
