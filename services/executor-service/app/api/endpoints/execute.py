from fastapi import APIRouter, HTTPException
from app.schemas.execute import TestRunRequest, TestRunParallelRequest, TestRunContainerRequest, TestDistributeRequest
from app.schemas.execute import TestRunResponse, TestRunParallelResponse, TestRunContainerResponse, TestDistributeResponse
from app.core.executor import TestExecutor
import asyncio

router = APIRouter()

# 初始化测试执行器
test_executor = TestExecutor()

@router.post("/run", response_model=TestRunResponse)
async def run_test(request: TestRunRequest):
    """执行单个测试
    
    接收测试命令和环境信息，执行单个测试。
    
    Args:
        request (TestRunRequest): 包含测试命令、测试类型和环境信息的请求
        
    Returns:
        TestRunResponse: 包含测试执行结果的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试执行器执行单个测试
        result = await test_executor.run_test(
            test_command=request.command,
            test_type=request.test_type,
            environment=request.environment
        )
        return TestRunResponse(result=result)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-parallel", response_model=TestRunParallelResponse)
async def run_tests_in_parallel(request: TestRunParallelRequest):
    """并行执行多个测试
    
    接收测试列表，并行执行多个测试。
    
    Args:
        request (TestRunParallelRequest): 包含测试列表的请求
        
    Returns:
        TestRunParallelResponse: 包含测试执行结果列表的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试执行器并行执行多个测试
        results = await test_executor.run_tests_in_parallel(request.tests)
        return TestRunParallelResponse(results=results)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-container", response_model=TestRunContainerResponse)
async def run_test_in_container(request: TestRunContainerRequest):
    """在Docker容器中执行测试
    
    接收测试命令、Docker镜像和挂载卷信息，在Docker容器中执行测试。
    
    Args:
        request (TestRunContainerRequest): 包含测试命令、Docker镜像和挂载卷信息的请求
        
    Returns:
        TestRunContainerResponse: 包含测试执行结果的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试执行器在Docker容器中执行测试
        result = test_executor.run_test_in_container(
            test_command=request.command,
            image=request.image,
            volumes=request.volumes
        )
        return TestRunContainerResponse(result=result)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/distribute", response_model=TestDistributeResponse)
async def distribute_tests(request: TestDistributeRequest):
    """将测试分发到多个节点
    
    接收测试列表和节点列表，将测试分发到多个节点。
    
    Args:
        request (TestDistributeRequest): 包含测试列表和节点列表的请求
        
    Returns:
        TestDistributeResponse: 包含测试分发结果的响应
        
    Raises:
        HTTPException: 如果处理过程中发生错误
    """
    try:
        # 调用测试执行器分发测试
        distribution = test_executor.distribute_tests(
            tests=request.tests,
            nodes=request.nodes
        )
        return TestDistributeResponse(distribution=distribution)
    except Exception as e:
        # 处理异常并返回错误信息
        raise HTTPException(status_code=500, detail=str(e))