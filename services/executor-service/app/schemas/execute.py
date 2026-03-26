from pydantic import BaseModel
from typing import List, Dict, Any

class TestRunRequest(BaseModel):
    command: str
    test_type: str
    environment: Dict[str, Any] = None

class TestRunResponse(BaseModel):
    result: Dict[str, Any]

class TestRunParallelRequest(BaseModel):
    tests: List[Dict[str, Any]]

class TestRunParallelResponse(BaseModel):
    results: List[Dict[str, Any]]

class TestRunContainerRequest(BaseModel):
    command: str
    image: str
    volumes: List[str] = None

class TestRunContainerResponse(BaseModel):
    result: Dict[str, Any]

class TestDistributeRequest(BaseModel):
    tests: List[Dict[str, Any]]
    nodes: List[str]

class TestDistributeResponse(BaseModel):
    distribution: Dict[str, List[Dict[str, Any]]]