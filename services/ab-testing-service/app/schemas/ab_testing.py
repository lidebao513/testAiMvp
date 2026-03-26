from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TestStrategyCreate(BaseModel):
    name: str
    type: str  # traditional, ai-enhanced, hybrid
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class TestExecutionCreate(BaseModel):
    strategies: List[str]
    test_suite: str
    execution_time: float
    environment: Optional[str] = None

class TestResult(BaseModel):
    test_id: str
    strategy_name: str
    defect_discovery_rate: float
    execution_time: float
    maintenance_cost: float
    status: str
    executed_at: datetime

class ABTestReport(BaseModel):
    report_id: str
    test_id: str
    generated_at: datetime
    strategies: List[str]
    results: List[TestResult]
    best_strategy: str
    metrics_comparison: Dict[str, Dict[str, float]]
    recommendations: List[str]

class StrategyComparison(BaseModel):
    strategies: List[str]
    metrics: Dict[str, Dict[str, float]]
    best_by_metric: Dict[str, str]
    overall_best: str
