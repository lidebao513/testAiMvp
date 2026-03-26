from pydantic import BaseModel
from typing import List, Dict, Any

class RequirementParseRequest(BaseModel):
    requirement_text: str

class RequirementParseResponse(BaseModel):
    test_points: List[Dict[str, Any]]

class CodeDiffAnalyzeRequest(BaseModel):
    diff_text: str

class CodeDiffAnalyzeResponse(BaseModel):
    test_cases: List[Dict[str, Any]]

class OpenAPIParseRequest(BaseModel):
    openapi_spec: Dict[str, Any]

class OpenAPIParseResponse(BaseModel):
    test_cases: List[Dict[str, Any]]