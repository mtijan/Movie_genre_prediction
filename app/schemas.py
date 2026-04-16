from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import Dict


class PredictRequest(BaseModel):
    overview: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Sinopsis atau deskripsi film dalam bahasa Inggris.",
        examples=["A group of elite soldiers are sent on a dangerous mission deep in enemy territory."],
    )


class PredictResponse(BaseModel):
    genre: str = Field(..., description="Genre yang diprediksi.")
    confidence: float = Field(..., description="Skor confidence (0.0 – 1.0).")
    all_scores: Dict[str, float] = Field(
        ..., description="Skor untuk setiap genre yang didukung."
    )


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    supported_genres: list


class InfoResponse(BaseModel):
    name: str
    version: str
    description: str
    endpoints: Dict[str, str]
