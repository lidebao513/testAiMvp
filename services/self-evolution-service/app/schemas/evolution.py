from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class FeedbackCreate(BaseModel):
    test_case_id: str
    quality_score: int = Field(ge=1, le=5)
    comments: Optional[str] = None
    reviewer: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    test_case_id: str
    quality_score: int
    comments: Optional[str]
    reviewer: Optional[str]
    created_at: datetime

class ExecutionResultCreate(BaseModel):
    test_case_id: str
    status: str
    is_real_defect: bool
    defect_details: Optional[str] = None
    execution_time: float

class ExecutionResultResponse(BaseModel):
    id: str
    test_case_id: str
    status: str
    is_real_defect: bool
    defect_details: Optional[str]
    execution_time: float
    created_at: datetime

class ModelFineTuneRequest(BaseModel):
    model_name: str
    dataset_size: int = Field(ge=100, le=10000)
    epochs: int = Field(ge=1, le=100)
    learning_rate: float = Field(ge=0.0001, le=0.1)

class EvolutionReport(BaseModel):
    report_id: str
    generated_at: datetime
    model_version: str
    previous_version: str
    metrics: Dict[str, float]
    improvements: List[str]
    recommendations: List[str]
    feedback_summary: Dict[str, Any]
    execution_summary: Dict[str, Any]
