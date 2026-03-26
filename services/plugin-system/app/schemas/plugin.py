from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PluginBase(BaseModel):
    name: str
    description: str
    category: str
    platform: str
    version: str
    author: str

class PluginCreate(PluginBase):
    templates: Optional[List[Dict[str, Any]]] = []
    strategies: Optional[List[Dict[str, Any]]] = []

class PluginUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    platform: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None

class PluginResponse(PluginBase):
    id: str
    templates: List[Dict[str, Any]] = []
    strategies: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True

class PluginTemplateBase(BaseModel):
    id: str
    name: str
    type: str
    content: str
    description: Optional[str] = None

class PluginTemplateCreate(PluginTemplateBase):
    pass

class PluginTemplateUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None

class PluginStrategyBase(BaseModel):
    id: str
    name: str
    type: str
    configuration: Dict[str, Any]
    description: Optional[str] = None

class PluginStrategyCreate(PluginStrategyBase):
    pass

class PluginStrategyUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    description: Optional[str] = None