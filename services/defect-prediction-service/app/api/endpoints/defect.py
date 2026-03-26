from fastapi import APIRouter, HTTPException, Depends
from app.core.defect_predictor import DefectPredictor
from app.schemas.defect import (
    AnalyzeCodeChangesRequest,
    AnalyzeCodeChangesResponse,
    HighRiskModule,
    FailureData,
    RootCauseAnalysisResponse,
    SimilarDefect,
    DefectData,
    DefectReportResponse,
    AnalyzeDependenciesRequest,
    AnalyzeDependenciesResponse,
    DependencyGraphAnalysis,
    DefectsListResponse,
    CodeHistoryResponse
)
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

router = APIRouter()

# 初始化缺陷预测器
api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

defect_predictor = DefectPredictor(api_key=api_key)

@router.post("/analyze/code-changes", response_model=AnalyzeCodeChangesResponse)
async def analyze_code_changes(request: AnalyzeCodeChangesRequest):
    """分析代码变更历史，预测高风险模块"""
    try:
        result = defect_predictor.analyze_code_changes(repo_path=request.repo_path)
        
        # 转换高风险模块格式
        high_risk_modules = []
        for module in result.get("high_risk_modules", []):
            high_risk_modules.append(HighRiskModule(
                file_path=module["file_path"],
                risk_score=module["risk_score"],
                changes=module["changes"],
                total_changes=module["total_changes"],
                last_changed=module["last_changed"]
            ))
        
        return AnalyzeCodeChangesResponse(
            high_risk_modules=high_risk_modules,
            total_commits_analyzed=result.get("total_commits_analyzed", 0),
            total_files_analyzed=result.get("total_files_analyzed", 0),
            error=result.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/root-cause", response_model=RootCauseAnalysisResponse)
async def analyze_root_cause(failure_data: FailureData):
    """测试失败时自动分析根因"""
    try:
        result = defect_predictor.analyze_failure_root_cause(failure_data.dict())
        
        # 转换相似缺陷格式
        similar_defects = []
        for defect in result.get("similar_defects", []):
            similar_defects.append(SimilarDefect(
                id=defect["id"],
                title=defect["title"],
                root_cause=defect["root_cause"]
            ))
        
        return RootCauseAnalysisResponse(
            root_cause=result.get("root_cause", "Unknown"),
            possible_fixes=result.get("possible_fixes", []),
            prevention_measures=result.get("prevention_measures", []),
            confidence=result.get("confidence", 0.0),
            similar_defects=similar_defects,
            error=result.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/report", response_model=DefectReportResponse)
async def generate_defect_report(defect_data: DefectData):
    """生成缺陷报告"""
    try:
        report = defect_predictor.generate_defect_report(defect_data.dict())
        
        return DefectReportResponse(
            id=report.id,
            title=report.title,
            description=report.description,
            root_cause=report.root_cause,
            severity=report.severity,
            impact=report.impact,
            reproduction_steps=report.reproduction_steps,
            suggested_fix=report.suggested_fix,
            similar_defects=report.similar_defects,
            timestamp=report.timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/dependencies", response_model=AnalyzeDependenciesResponse)
async def analyze_dependencies(request: AnalyzeDependenciesRequest):
    """使用图神经网络分析代码依赖关系"""
    try:
        result = defect_predictor.analyze_code_dependencies(code_path=request.code_path)
        
        if "error" in result:
            return AnalyzeDependenciesResponse(
                dependency_graph=DependencyGraphAnalysis(
                    centrality={},
                    depths={},
                    key_nodes=[],
                    cycles=[]
                ),
                node_count=0,
                edge_count=0,
                error=result["error"]
            )
        
        return AnalyzeDependenciesResponse(
            dependency_graph=DependencyGraphAnalysis(
                centrality=result["dependency_graph"]["centrality"],
                depths=result["dependency_graph"]["depths"],
                key_nodes=result["dependency_graph"]["key_nodes"],
                cycles=result["dependency_graph"]["cycles"]
            ),
            node_count=result["node_count"],
            edge_count=result["edge_count"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/defects", response_model=DefectsListResponse)
async def get_defects():
    """获取所有缺陷报告"""
    try:
        defects = defect_predictor.get_defects()
        
        defect_list = []
        for defect in defects:
            defect_list.append(DefectReportResponse(
                id=defect.id,
                title=defect.title,
                description=defect.description,
                root_cause=defect.root_cause,
                severity=defect.severity,
                impact=defect.impact,
                reproduction_steps=defect.reproduction_steps,
                suggested_fix=defect.suggested_fix,
                similar_defects=defect.similar_defects,
                timestamp=defect.timestamp
            ))
        
        return DefectsListResponse(defects=defect_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/code-history", response_model=CodeHistoryResponse)
async def get_code_history():
    """获取代码历史数据"""
    try:
        history = defect_predictor.get_code_history()
        
        return CodeHistoryResponse(
            commits=history.get("commits", []),
            file_changes=history.get("file_changes", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))