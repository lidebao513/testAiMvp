from fastapi import APIRouter, HTTPException
from app.schemas.parse import RequirementParseRequest, CodeDiffAnalyzeRequest, OpenAPIParseRequest
from app.schemas.parse import RequirementParseResponse, CodeDiffAnalyzeResponse, OpenAPIParseResponse
from app.core.nlp_parser import NLPParser
import os

router = APIRouter()

# 初始化NLP解析器
api_key = os.getenv("OPENAI_API_KEY", "")  # 从环境变量获取OpenAI API密钥
model = os.getenv("AI_MODEL", "gpt-4")  # 从环境变量获取AI模型名称
nlp_parser = NLPParser(api_key=api_key, model=model)

@router.post("/requirement", response_model=RequirementParseResponse)
async def parse_requirement(request: RequirementParseRequest):
    """解析需求文档并提取测试点
    
    接收需求文档文本，使用NLP解析器提取测试点。
    
    Args:
        request (RequirementParseRequest): 包含需求文档文本的请求
        
    Returns:
        RequirementParseResponse: 包含提取的测试点的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用NLP解析器提取测试点
        test_points = nlp_parser.extract_test_points(request.requirement_text)
        return RequirementParseResponse(test_points=test_points)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/code-diff", response_model=CodeDiffAnalyzeResponse)
async def analyze_code_diff(request: CodeDiffAnalyzeRequest):
    """分析代码变更并识别需要的测试用例
    
    接收代码变更的diff文本，使用NLP解析器分析并识别需要更新或添加的测试用例。
    
    Args:
        request (CodeDiffAnalyzeRequest): 包含代码变更diff文本的请求
        
    Returns:
        CodeDiffAnalyzeResponse: 包含识别的测试用例的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用NLP解析器分析代码变更
        test_cases = nlp_parser.analyze_code_diff(request.diff_text)
        return CodeDiffAnalyzeResponse(test_cases=test_cases)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/openapi", response_model=OpenAPIParseResponse)
async def parse_openapi(request: OpenAPIParseRequest):
    """解析OpenAPI规范并生成测试用例
    
    接收OpenAPI规范，解析并生成对应的测试用例。
    
    Args:
        request (OpenAPIParseRequest): 包含OpenAPI规范的请求
        
    Returns:
        OpenAPIParseResponse: 包含生成的测试用例的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用NLP解析器解析OpenAPI规范
        test_cases = nlp_parser.parse_openapi_spec(request.openapi_spec)
        return OpenAPIParseResponse(test_cases=test_cases)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))