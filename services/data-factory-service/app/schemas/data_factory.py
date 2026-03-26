from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class FieldConfig(BaseModel):
    type: str
    options: Optional[Dict[str, Any]] = {}
    depends_on: Optional[List[str]] = []

class DataSchemaCreate(BaseModel):
    name: str
    description: str
    fields: Dict[str, FieldConfig]
    sensitive_fields: Optional[List[str]] = []

class DataSchemaResponse(BaseModel):
    id: str
    name: str
    description: str
    fields: Dict[str, FieldConfig]
    sensitive_fields: List[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class DataGenerateRequest(BaseModel):
    schema_id: str
    count: int = 1
    parameters: Optional[Dict[str, Any]] = {}

class DataGenerateResponse(BaseModel):
    schema_id: str
    version_id: str
    data: List[Dict[str, Any]]
    count: int

class DataVersionResponse(BaseModel):
    id: str
    schema_id: str
    version: int
    created_at: str
    
    class Config:
        from_attributes = True

class DataRollbackRequest(BaseModel):
    schema_id: str
    version_id: str