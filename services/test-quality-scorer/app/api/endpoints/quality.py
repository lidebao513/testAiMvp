from fastapi import APIRouter, HTTPException
from app.core.quality_scorer import QualityScorer
from app.schemas.quality import (
    TestCaseCreate,
    QualityScore,
    TrainingDataCreate,
    ModelTrainingRequest
)

router = APIRouter()
quality_scorer = QualityScorer()

@router.post("/score", response_model=QualityScore)
async def score_test_case(test_case: TestCaseCreate):
    """评估测试用例质量"""
    try:
        score = quality_scorer.score_test_case(test_case.dict())
        return QualityScore(**score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def train_model(request: ModelTrainingRequest):
    """训练质量评分模型"""
    try:
        result = quality_scorer.train_model(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-training-data")
async def add_training_data(data: TrainingDataCreate):
    """添加训练数据"""
    try:
        result = quality_scorer.add_training_data(data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-status")
async def get_model_status():
    """获取模型状态"""
    try:
        status = quality_scorer.get_model_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quality-stats")
async def get_quality_stats():
    """获取质量统计信息"""
    try:
        stats = quality_scorer.get_quality_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
