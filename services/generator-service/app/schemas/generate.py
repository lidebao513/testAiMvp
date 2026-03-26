from pydantic import BaseModel
from typing import List, Dict, Any

class UnitTestGenerateRequest(BaseModel):
    code: str
    language: str = "python"

class UnitTestGenerateResponse(BaseModel):
    test_code: str

class IntegrationTestGenerateRequest(BaseModel):
    api_spec: Dict[str, Any]

class IntegrationTestGenerateResponse(BaseModel):
    test_code: str

class E2ETestGenerateRequest(BaseModel):
    user_flow: str
    framework: str = "playwright"

class E2ETestGenerateResponse(BaseModel):
    test_code: str

class TestDataGenerateRequest(BaseModel):
    schema: Dict[str, Any]

class TestDataGenerateResponse(BaseModel):
    test_data: List[Dict[str, Any]]