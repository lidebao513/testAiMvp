from fastapi import APIRouter, HTTPException
from app.schemas.knowledge import (
    DefectAddRequest, TestPatternAddRequest, BestPracticeAddRequest, SimilarSearchRequest,
    DefectAddResponse, TestPatternAddResponse, BestPracticeAddResponse, SimilarSearchResponse,
    TestCaseAddRequest, TestCaseAddResponse, DefectPatternAddRequest, DefectPatternAddResponse,
    SearchTestCasesRequest, SearchTestCasesResponse, SearchDefectsRequest, SearchDefectsResponse,
    RAGRequest, RAGResponse, GetTestCasesRequest, GetTestCasesResponse,
    GetDefectPatternsRequest, GetDefectPatternsResponse
)
from app.core.knowledge_base import KnowledgeBase
import os

router = APIRouter()

# 初始化知识库
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # 从环境变量获取MongoDB连接URI
milvus_uri = os.getenv("MILVUS_URI", "localhost:19530")  # 从环境变量获取Milvus连接URI
openai_api_key = os.getenv("OPENAI_API_KEY", "")  # 从环境变量获取OpenAI API密钥
local_embedding_url = os.getenv("LOCAL_EMBEDDING_URL", "")  # 从环境变量获取本地嵌入模型URL

knowledge_base = KnowledgeBase(
    mongo_uri=mongo_uri, 
    milvus_uri=milvus_uri,
    openai_api_key=openai_api_key,
    local_embedding_url=local_embedding_url
)

@router.post("/add-defect", response_model=DefectAddResponse)
async def add_defect(request: DefectAddRequest):
    """添加缺陷到知识库
    
    接收缺陷信息，添加到知识库中。
    
    Args:
        request (DefectAddRequest): 包含缺陷信息的请求
        
    Returns:
        DefectAddResponse: 包含缺陷ID的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库添加缺陷
        defect_id = knowledge_base.add_defect(request.defect)
        return DefectAddResponse(defect_id=defect_id)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-defects")
async def get_defects():
    """获取缺陷列表
    
    从知识库中获取所有缺陷。
    
    Returns:
        List[Dict[str, Any]]: 缺陷列表
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库获取缺陷列表
        defects = knowledge_base.get_defects()
        return defects
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-test-pattern", response_model=TestPatternAddResponse)
async def add_test_pattern(request: TestPatternAddRequest):
    """添加测试模式到知识库
    
    接收测试模式信息，添加到知识库中。
    
    Args:
        request (TestPatternAddRequest): 包含测试模式信息的请求
        
    Returns:
        TestPatternAddResponse: 包含测试模式ID的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库添加测试模式
        pattern_id = knowledge_base.add_test_pattern(request.pattern)
        return TestPatternAddResponse(pattern_id=pattern_id)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-test-patterns")
async def get_test_patterns():
    """获取测试模式列表
    
    从知识库中获取所有测试模式。
    
    Returns:
        List[Dict[str, Any]]: 测试模式列表
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库获取测试模式列表
        patterns = knowledge_base.get_test_patterns()
        return patterns
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-best-practice", response_model=BestPracticeAddResponse)
async def add_best_practice(request: BestPracticeAddRequest):
    """添加最佳实践到知识库
    
    接收最佳实践信息，添加到知识库中。
    
    Args:
        request (BestPracticeAddRequest): 包含最佳实践信息的请求
        
    Returns:
        BestPracticeAddResponse: 包含最佳实践ID的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库添加最佳实践
        practice_id = knowledge_base.add_best_practice(request.practice)
        return BestPracticeAddResponse(practice_id=practice_id)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-best-practices")
async def get_best_practices():
    """获取最佳实践列表
    
    从知识库中获取所有最佳实践。
    
    Returns:
        List[Dict[str, Any]]: 最佳实践列表
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库获取最佳实践列表
        practices = knowledge_base.get_best_practices()
        return practices
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-similar", response_model=SimilarSearchResponse)
async def search_similar(request: SimilarSearchRequest):
    """搜索相似的知识
    
    接收查询向量，在知识库中搜索相似的知识。
    
    Args:
        request (SimilarSearchRequest): 包含查询向量和返回结果数量的请求
        
    Returns:
        SimilarSearchResponse: 包含相似知识列表的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库搜索相似知识
        similar_items = knowledge_base.search_similar(request.query_embedding, request.top_k)
        return SimilarSearchResponse(similar_items=similar_items)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-test-case", response_model=TestCaseAddResponse)
async def add_test_case(request: TestCaseAddRequest):
    """添加测试用例到知识库
    
    接收测试用例信息，添加到知识库中。
    
    Args:
        request (TestCaseAddRequest): 包含测试用例信息的请求
        
    Returns:
        TestCaseAddResponse: 包含测试用例ID的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库添加测试用例
        test_case_id = knowledge_base.add_test_case(request.test_case)
        return TestCaseAddResponse(test_case_id=test_case_id)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-defect-pattern", response_model=DefectPatternAddResponse)
async def add_defect_pattern(request: DefectPatternAddRequest):
    """添加缺陷模式到知识库
    
    接收缺陷模式信息，添加到知识库中。
    
    Args:
        request (DefectPatternAddRequest): 包含缺陷模式信息的请求
        
    Returns:
        DefectPatternAddResponse: 包含缺陷模式ID的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库添加缺陷模式
        defect_pattern_id = knowledge_base.add_defect_pattern(request.defect_pattern)
        return DefectPatternAddResponse(defect_pattern_id=defect_pattern_id)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-test-cases", response_model=SearchTestCasesResponse)
async def search_test_cases(request: SearchTestCasesRequest):
    """搜索相似的测试用例
    
    接收查询文本，在知识库中搜索相似的测试用例。
    
    Args:
        request (SearchTestCasesRequest): 包含查询文本、返回结果数量和可选类别的请求
        
    Returns:
        SearchTestCasesResponse: 包含相似测试用例列表的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库搜索相似测试用例
        similar_test_cases = knowledge_base.search_similar_test_cases(
            request.query,
            request.top_k,
            request.category
        )
        return SearchTestCasesResponse(similar_test_cases=similar_test_cases)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-defects", response_model=SearchDefectsResponse)
async def search_defects(request: SearchDefectsRequest):
    """搜索相似的缺陷
    
    接收查询文本，在知识库中搜索相似的缺陷和缺陷模式。
    
    Args:
        request (SearchDefectsRequest): 包含查询文本和返回结果数量的请求
        
    Returns:
        SearchDefectsResponse: 包含相似缺陷列表的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库搜索相似缺陷
        similar_defects = knowledge_base.search_similar_defects(
            request.query,
            request.top_k
        )
        return SearchDefectsResponse(similar_defects=similar_defects)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rag-enhanced", response_model=RAGResponse)
async def rag_enhanced(request: RAGRequest):
    """检索增强生成 (RAG) 提升测试生成质量
    
    接收查询文本，检索相关知识作为上下文，增强生成质量。
    
    Args:
        request (RAGRequest): 包含查询文本和上下文大小的请求
        
    Returns:
        RAGResponse: 包含检索到的上下文和增强提示的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库进行RAG增强
        rag_result = knowledge_base.rag_enhanced_generation(
            request.query,
            request.context_size
        )
        return RAGResponse(**rag_result)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-test-cases")
async def get_test_cases():
    """获取测试用例列表
    
    从知识库中获取所有测试用例。
    
    Returns:
        List[Dict[str, Any]]: 测试用例列表
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库获取测试用例列表
        test_cases = knowledge_base.get_test_cases()
        return test_cases
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-defect-patterns")
async def get_defect_patterns():
    """获取缺陷模式列表
    
    从知识库中获取所有缺陷模式。
    
    Returns:
        List[Dict[str, Any]]: 缺陷模式列表
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用知识库获取缺陷模式列表
        defect_patterns = knowledge_base.get_defect_patterns()
        return defect_patterns
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))