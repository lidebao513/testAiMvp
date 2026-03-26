from fastapi import APIRouter, HTTPException
from app.core.data_factory import DataFactory
from app.schemas.data_factory import (
    DataSchemaCreate,
    DataSchemaResponse,
    DataGenerateRequest,
    DataGenerateResponse,
    DataVersionResponse,
    DataRollbackRequest
)

router = APIRouter()
data_factory = DataFactory()

@router.post("/schemas", response_model=DataSchemaResponse)
async def create_data_schema(schema: DataSchemaCreate):
    """创建数据模式"""
    try:
        result = data_factory.create_schema(schema.dict())
        return DataSchemaResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schemas", response_model=list[DataSchemaResponse])
async def get_data_schemas():
    """获取所有数据模式"""
    try:
        schemas = data_factory.get_schemas()
        return [DataSchemaResponse(**schema) for schema in schemas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schemas/{schema_id}", response_model=DataSchemaResponse)
async def get_data_schema(schema_id: str):
    """获取数据模式详情"""
    try:
        schema = data_factory.get_schema(schema_id)
        return DataSchemaResponse(**schema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=DataGenerateResponse)
async def generate_data(request: DataGenerateRequest):
    """生成测试数据"""
    try:
        result = data_factory.generate_data(request.schema_id, request.count, request.parameters)
        return DataGenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/versions/{schema_id}", response_model=list[DataVersionResponse])
async def get_data_versions(schema_id: str):
    """获取数据版本历史"""
    try:
        versions = data_factory.get_versions(schema_id)
        return [DataVersionResponse(**version) for version in versions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rollback")
async def rollback_data(request: DataRollbackRequest):
    """回滚数据版本"""
    try:
        result = data_factory.rollback_version(request.schema_id, request.version_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-dependencies")
async def analyze_dependencies(schema_id: str):
    """分析数据依赖关系"""
    try:
        result = data_factory.analyze_dependencies(schema_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))