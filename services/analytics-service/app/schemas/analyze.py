from pydantic import BaseModel
from typing import List, Dict, Any

class CoverageAnalyzeRequest(BaseModel):
    coverage_data: Dict[str, Any]

class CoverageAnalyzeResponse(BaseModel):
    report: Dict[str, Any]

class DefectPredictRequest(BaseModel):
    code_change: str

class DefectPredictResponse(BaseModel):
    defects: List[Dict[str, Any]]

class TestPrioritizeRequest(BaseModel):
    test_cases: List[Dict[str, Any]]

class TestPrioritizeResponse(BaseModel):
    prioritized_tests: List[Dict[str, Any]]

class FailureAnalyzeRequest(BaseModel):
    failure_data: Dict[str, Any]

class FailureAnalyzeResponse(BaseModel):
    analysis: Dict[str, Any]