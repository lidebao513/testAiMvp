from fastapi import APIRouter, HTTPException
from app.core.ab_testing import ABTestingEngine
from app.schemas.ab_testing import (
    TestStrategyCreate,
    TestExecutionCreate,
    TestResult,
    ABTestReport,
    StrategyComparison
)

router = APIRouter()
ab_testing_engine = ABTestingEngine()

@router.post("/strategies")
async def create_test_strategy(strategy: TestStrategyCreate):
    """创建测试策略"""
    try:
        result = ab_testing_engine.create_strategy(strategy.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_test_strategies():
    """获取所有测试策略"""
    try:
        strategies = ab_testing_engine.get_strategies()
        return {"strategies": strategies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_ab_test(execution: TestExecutionCreate):
    """执行A/B测试"""
    try:
        result = ab_testing_engine.execute_ab_test(execution.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{test_id}")
async def get_ab_test_report(test_id: str):
    """获取A/B测试报告"""
    try:
        report = ab_testing_engine.generate_report(test_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def get_all_reports():
    """获取所有A/B测试报告"""
    try:
        reports = ab_testing_engine.get_all_reports()
        return {"reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/best-strategy")
async def get_best_strategy():
    """获取最优策略"""
    try:
        best_strategy = ab_testing_engine.get_best_strategy()
        return best_strategy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategy-comparison")
async def get_strategy_comparison():
    """获取策略对比"""
    try:
        comparison = ab_testing_engine.compare_strategies()
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
