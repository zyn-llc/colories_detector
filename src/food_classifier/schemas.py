from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TopKPrediction(BaseModel):
    food: str
    class_index: int
    confidence: float = Field(ge=0.0, le=1.0)


class PredictionResult(BaseModel):
    status: Literal["recognized", "unknown", "invalid_input"]
    prediction: str | None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    top_3: list[TopKPrediction]
    model_version: str
    error: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model: str
    version: str
