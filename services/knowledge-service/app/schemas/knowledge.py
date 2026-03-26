from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DefectAddRequest(BaseModel):
    defect: Dict[str, Any]

class DefectAddResponse(BaseModel):
    defect_id: str

class TestPatternAddRequest(BaseModel):
    pattern: Dict[str, Any]

class TestPatternAddResponse(BaseModel):
    pattern_id: str

class BestPracticeAddRequest(BaseModel):
    practice: Dict[str, Any]

class BestPracticeAddResponse(BaseModel):
    practice_id: str

class TestCaseAddRequest(BaseModel):
    test_case: Dict[str, Any]

class TestCaseAddResponse(BaseModel):
    test_case_id: str

class DefectPatternAddRequest(BaseModel):
    defect_pattern: Dict[str, Any]

class DefectPatternAddResponse(BaseModel):
    defect_pattern_id: str

class SimilarSearchRequest(BaseModel):
    query_embedding: List[float]
    top_k: int = 5

class SimilarSearchResponse(BaseModel):
    similar_items: List[Dict[str, Any]]

class SearchTestCasesRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    category: Optional[str] = None

class SearchTestCasesResponse(BaseModel):
    similar_test_cases: List[Dict[str, Any]]

class SearchDefectsRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class SearchDefectsResponse(BaseModel):
    similar_defects: List[Dict[str, Any]]

class RAGRequest(BaseModel):
    query: str
    context_size: Optional[int] = 3

class RAGResponse(BaseModel):
    query: str
    context: List[Dict[str, Any]]
    enhanced_prompt: str

class GetTestCasesRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = None

class GetTestCasesResponse(BaseModel):
    test_cases: List[Dict[str, Any]]

class GetDefectPatternsRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = None

class GetDefectPatternsResponse(BaseModel):
    defect_patterns: List[Dict[str, Any]]