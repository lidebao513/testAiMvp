from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TestCaseCreate(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    type: str  # unit, api, e2e
    language: str  # python, javascript, java, etc.

class QualityScore(BaseModel):
    test_case_id: str
    overall_score: float = Field(ge=0, le=100)
    readability: float = Field(ge=0, le=100)
    completeness: float = Field(ge=0, le=100)
    independence: float = Field(ge=0, le=100)
    effectiveness: float = Field(ge=0, le=100)
    feedback: List[str]
    scored_at: datetime

class TrainingDataCreate(BaseModel):
    test_case: TestCaseCreate
    readability_score: float = Field(ge=0, le=100)
    completeness_score: float = Field(ge=0, le=100)
    independence_score: float = Field(ge=0, le=100)
    effectiveness_score: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)
    reviewer: Optional[str] = None

class ModelTrainingRequest(BaseModel):
    epochs: int = Field(ge=1, le=100)
    learning_rate: float = Field(ge=0.0001, le=0.1)
    test_size: float = Field(ge=0.1, le=0.5)
    model_type: str = "random_forest"  # random_forest, svm, xgboost
