from fastapi import APIRouter, HTTPException
from app.schemas.analyze import CoverageAnalyzeRequest, DefectPredictRequest, TestPrioritizeRequest, FailureAnalyzeRequest
from app.schemas.analyze import CoverageAnalyzeResponse, DefectPredictResponse, TestPrioritizeResponse, FailureAnalyzeResponse
from app.core.analyzer import TestAnalyzer
import os

router = APIRouter()

# 初始化测试分析器
api_key = os.getenv("OPENAI_API_KEY", "")  # 从环境变量获取OpenAI API密钥
model = os.getenv("AI_MODEL", "gpt-4")  # 从环境变量获取AI模型名称
test_analyzer = TestAnalyzer(api_key=api_key, model=model)

@router.post("/coverage", response_model=CoverageAnalyzeResponse)
async def analyze_coverage(request: CoverageAnalyzeRequest):
    """分析测试覆盖率
    
    接收覆盖率数据，分析并生成覆盖率报告。
    
    Args:
        request (CoverageAnalyzeRequest): 包含覆盖率数据的请求
        
    Returns:
        CoverageAnalyzeResponse: 包含覆盖率报告的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试分析器分析覆盖率
        report = test_analyzer.analyze_coverage(request.coverage_data)
        return CoverageAnalyzeResponse(report=report)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-defects", response_model=DefectPredictResponse)
async def predict_defects(request: DefectPredictRequest):
    """预测潜在缺陷
    
    接收代码变更，预测可能存在的缺陷。
    
    Args:
        request (DefectPredictRequest): 包含代码变更的请求
        
    Returns:
        DefectPredictResponse: 包含预测的缺陷列表的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试分析器预测缺陷
        defects = test_analyzer.predict_defects(request.code_change)
        return DefectPredictResponse(defects=defects)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prioritize-tests", response_model=TestPrioritizeResponse)
async def prioritize_tests(request: TestPrioritizeRequest):
    """对测试用例进行优先级排序
    
    接收测试用例列表，基于风险和影响进行优先级排序。
    
    Args:
        request (TestPrioritizeRequest): 包含测试用例列表的请求
        
    Returns:
        TestPrioritizeResponse: 包含按优先级排序的测试用例列表的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试分析器对测试用例进行优先级排序
        prioritized_tests = test_analyzer.prioritize_test_cases(request.test_cases)
        return TestPrioritizeResponse(prioritized_tests=prioritized_tests)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-failure", response_model=FailureAnalyzeResponse)
async def analyze_failure(request: FailureAnalyzeRequest):
    """分析测试失败的根因
    
    接收测试失败数据，分析根因并提供修复建议。
    
    Args:
        request (FailureAnalyzeRequest): 包含测试失败数据的请求
        
    Returns:
        FailureAnalyzeResponse: 包含根因分析结果的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试分析器分析失败根因
        analysis = test_analyzer.analyze_failure_root_cause(request.failure_data)
        return FailureAnalyzeResponse(analysis=analysis)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))