from fastapi import APIRouter, HTTPException
from app.schemas.generate import UnitTestGenerateRequest, IntegrationTestGenerateRequest, E2ETestGenerateRequest, TestDataGenerateRequest
from app.schemas.generate import UnitTestGenerateResponse, IntegrationTestGenerateResponse, E2ETestGenerateResponse, TestDataGenerateResponse
from app.core.test_generator import TestGenerator
import os

router = APIRouter()

# 初始化测试生成器
api_key = os.getenv("OPENAI_API_KEY", "")  # 从环境变量获取OpenAI API密钥
model = os.getenv("AI_MODEL", "gpt-4")  # 从环境变量获取AI模型名称
test_generator = TestGenerator(api_key=api_key, model=model)

@router.post("/unit-test", response_model=UnitTestGenerateResponse)
async def generate_unit_test(request: UnitTestGenerateRequest):
    """生成单元测试代码
    
    接收代码和语言信息，生成对应的单元测试代码。
    
    Args:
        request (UnitTestGenerateRequest): 包含代码和语言信息的请求
        
    Returns:
        UnitTestGenerateResponse: 包含生成的单元测试代码的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试生成器生成单元测试
        test_code = test_generator.generate_unit_test(request.code, request.language)
        return UnitTestGenerateResponse(test_code=test_code)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integration-test", response_model=IntegrationTestGenerateResponse)
async def generate_integration_test(request: IntegrationTestGenerateRequest):
    """生成API集成测试代码
    
    接收API规范，生成对应的集成测试代码。
    
    Args:
        request (IntegrationTestGenerateRequest): 包含API规范的请求
        
    Returns:
        IntegrationTestGenerateResponse: 包含生成的集成测试代码的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试生成器生成集成测试
        test_code = test_generator.generate_integration_test(request.api_spec)
        return IntegrationTestGenerateResponse(test_code=test_code)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/e2e-test", response_model=E2ETestGenerateResponse)
async def generate_e2e_test(request: E2ETestGenerateRequest):
    """生成E2E测试代码
    
    接收用户流程描述和测试框架，生成对应的E2E测试代码。
    
    Args:
        request (E2ETestGenerateRequest): 包含用户流程描述和测试框架的请求
        
    Returns:
        E2ETestGenerateResponse: 包含生成的E2E测试代码的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试生成器生成E2E测试
        test_code = test_generator.generate_e2e_test(request.user_flow, request.framework)
        return E2ETestGenerateResponse(test_code=test_code)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-data", response_model=TestDataGenerateResponse)
async def generate_test_data(request: TestDataGenerateRequest):
    """生成测试数据
    
    接收数据模式，生成对应的测试数据。
    
    Args:
        request (TestDataGenerateRequest): 包含数据模式的请求
        
    Returns:
        TestDataGenerateResponse: 包含生成的测试数据的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试生成器生成测试数据
        test_data = test_generator.generate_test_data(request.schema)
        return TestDataGenerateResponse(test_data=test_data)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))