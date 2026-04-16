"""
Prediction module for Movie Genre Prediction.
Loads LinearSVC model and TF-IDF vectorizer from local files.
"""

import os
import pickle
from pathlib import Path

# Path ke model & vectorizer
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "model.pkl"
VECTORIZER_PATH = BASE_DIR / "models" / "vectorizer.pkl"

_model = None
_vectorizer = None


def load_model():
    """Load model dan vectorizer dari file lokal. Cache setelah pertama kali load."""
    global _model, _vectorizer

    if _model is None or _vectorizer is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model tidak ditemukan di {MODEL_PATH}. "
                "Jalankan 'python src/train.py' terlebih dahulu."
            )
        if not VECTORIZER_PATH.exists():
            raise FileNotFoundError(
                f"Vectorizer tidak ditemukan di {VECTORIZER_PATH}. "
                "Jalankan 'python src/train.py' terlebih dahulu."
            )

        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        with open(VECTORIZER_PATH, "rb") as f:
            _vectorizer = pickle.load(f)

        print(f"[predict] Model loaded dari: {MODEL_PATH}")
        print(f"[predict] Vectorizer loaded dari: {VECTORIZER_PATH}")

    return _model, _vectorizer


def predict(overview: str) -> dict:
    """
    Prediksi genre dari teks overview film.

    Args:
        overview: Teks sinopsis/deskripsi film.

    Returns:
        dict dengan keys:
            - genre (str): Genre yang diprediksi
            - confidence (float): Skor confidence (dari decision function, dinormalisasi)
            - all_scores (dict): Skor untuk setiap genre
    """
    overview = overview.strip()
    if not overview:
        raise ValueError("Overview tidak boleh kosong.")

    model, vectorizer = load_model()

    # Vektorisasi teks
    X = vectorizer.transform([overview])

    # Prediksi label
    predicted_genre = model.predict(X)[0]

    # Decision function scores (LinearSVC tidak punya predict_proba)
    decision_scores = model.decision_function(X)[0]
    classes = model.classes_

    # Normalisasi skor ke rentang 0–1 menggunakan softmax-style
    import numpy as np

    exp_scores = np.exp(decision_scores - np.max(decision_scores))
    probabilities = exp_scores / exp_scores.sum()

    all_scores = {
        cls: round(float(prob), 4)
        for cls, prob in zip(classes, probabilities)
    }

    confidence = all_scores[predicted_genre]

    return {
        "genre": predicted_genre,
        "confidence": confidence,
        "all_scores": all_scores,
    }


def is_model_loaded() -> bool:
    """Cek apakah model sudah di-load."""
    return _model is not None and _vectorizer is not None


def get_supported_genres() -> list:
    """Mengembalikan daftar genre yang didukung model."""
    _, _ = load_model()
    return list(_model.classes_)


if __name__ == "__main__":
    # Quick test
    test_texts = [
        "A group of soldiers must fight through enemy territory to survive.",
        "Two best friends fall in love during an unexpected road trip.",
        "A young comedian tries to make it big in New York City.",
        "A family struggles with grief after the loss of a loved one.",
    ]

    print("=== Prediction Module Test ===\n")
    for text in test_texts:
        result = predict(text)
        print(f"Overview : {text[:60]}...")
        print(f"Genre    : {result['genre']} (confidence: {result['confidence']:.2%})")
        print(f"Scores   : {result['all_scores']}")
        print()
