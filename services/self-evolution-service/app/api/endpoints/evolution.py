from fastapi import APIRouter, HTTPException
from app.core.self_evolution import SelfEvolutionEngine
from app.schemas.evolution import (
    FeedbackCreate,
    ExecutionResultCreate,
    ModelFineTuneRequest,
    EvolutionReport,
    FeedbackResponse,
    ExecutionResultResponse
)

router = APIRouter()
evolution_engine = SelfEvolutionEngine()

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackCreate):
    """提交人工审核反馈"""
    try:
        result = evolution_engine.add_feedback(feedback.dict())
        return FeedbackResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execution-result", response_model=ExecutionResultResponse)
async def submit_execution_result(result: ExecutionResultCreate):
    """提交测试执行结果"""
    try:
        result = evolution_engine.add_execution_result(result.dict())
        return ExecutionResultResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fine-tune")
async def fine_tune_model(request: ModelFineTuneRequest):
    """微调模型"""
    try:
        result = evolution_engine.fine_tune_model(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report", response_model=EvolutionReport)
async def generate_evolution_report():
    """生成进化报告"""
    try:
        report = evolution_engine.generate_evolution_report()
        return EvolutionReport(**report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize-strategy")
async def optimize_generation_strategy():
    """优化生成策略"""
    try:
        result = evolution_engine.optimize_generation_strategy()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback-stats")
async def get_feedback_stats():
    """获取反馈统计信息"""
    try:
        stats = evolution_engine.get_feedback_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/execution-stats")
async def get_execution_stats():
    """获取执行统计信息"""
    try:
        stats = evolution_engine.get_execution_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
