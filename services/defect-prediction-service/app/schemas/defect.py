from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AnalyzeCodeChangesRequest(BaseModel):
    """分析代码变更请求"""
    repo_path: Optional[str] = None

class HighRiskModule(BaseModel):
    """高风险模块"""
    file_path: str
    risk_score: float
    changes: int
    total_changes: int
    last_changed: str

class AnalyzeCodeChangesResponse(BaseModel):
    """分析代码变更响应"""
    high_risk_modules: List[HighRiskModule]
    total_commits_analyzed: int
    total_files_analyzed: int
    error: Optional[str] = None

class FailureData(BaseModel):
    """测试失败数据"""
    test_name: str
    error: str
    stack_trace: Optional[str] = None
    environment: Optional[Dict[str, Any]] = None

class SimilarDefect(BaseModel):
    """相似缺陷"""
    id: str
    title: str
    root_cause: str

class RootCauseAnalysisResponse(BaseModel):
    """根因分析响应"""
    root_cause: str
    possible_fixes: List[str]
    prevention_measures: List[str]
    confidence: float
    similar_defects: List[SimilarDefect]
    error: Optional[str] = None

class DefectData(BaseModel):
    """缺陷数据"""
    title: Optional[str] = None
    description: Optional[str] = None
    error: Optional[str] = None
    stack_trace: Optional[str] = None
    environment: Optional[Dict[str, Any]] = None

class DefectReportResponse(BaseModel):
    """缺陷报告响应"""
    id: str
    title: str
    description: str
    root_cause: str
    severity: str
    impact: List[str]
    reproduction_steps: List[str]
    suggested_fix: str
    similar_defects: List[Any]
    timestamp: str

class AnalyzeDependenciesRequest(BaseModel):
    """分析依赖关系请求"""
    code_path: Optional[str] = None

class DependencyGraphAnalysis(BaseModel):
    """依赖图分析"""
    centrality: Dict[str, float]
    depths: Dict[str, int]
    key_nodes: List[str]
    cycles: List[List[str]]

class AnalyzeDependenciesResponse(BaseModel):
    """分析依赖关系响应"""
    dependency_graph: DependencyGraphAnalysis
    node_count: int
    edge_count: int
    error: Optional[str] = None

class DefectsListResponse(BaseModel):
    """缺陷列表响应"""
    defects: List[DefectReportResponse]

class CodeHistoryResponse(BaseModel):
    """代码历史响应"""
    commits: List[Dict[str, Any]]
    file_changes: Dict[str, Dict[str, Any]]