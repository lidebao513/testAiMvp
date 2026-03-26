from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class HealUILocatorRequest(BaseModel):
    """自愈UI元素定位请求"""
    test_id: str
    element_name: str
    page: str
    current_locator: Dict[str, str]
    page_source: str

class HealUILocatorResponse(BaseModel):
    """自愈UI元素定位响应"""
    success: bool
    new_locator: Optional[Dict[str, str]] = None
    message: str

class HealApiAssertionRequest(BaseModel):
    """自愈API断言请求"""
    test_id: str
    endpoint: str
    original_assertion: Dict[str, Any]
    actual_response: Dict[str, Any]

class HealApiAssertionResponse(BaseModel):
    """自愈API断言响应"""
    success: bool
    new_assertion: Optional[Dict[str, Any]] = None
    message: str

class HealTestDataRequest(BaseModel):
    """自愈测试数据请求"""
    test_id: str
    data_type: str
    original_data: Dict[str, Any]

class HealTestDataResponse(BaseModel):
    """自愈测试数据响应"""
    success: bool
    new_data: Optional[Dict[str, Any]] = None
    message: str

class HealingActionResponse(BaseModel):
    """自愈操作响应"""
    id: str
    type: str
    test_id: str
    original_value: Any
    new_value: Any
    timestamp: str
    confidence: float
    status: str

class ApproveActionRequest(BaseModel):
    """批准自愈操作请求"""
    action_id: str

class RejectActionRequest(BaseModel):
    """拒绝自愈操作请求"""
    action_id: str

class ActionResponse(BaseModel):
    """操作响应"""
    success: bool
    message: str

class KnowledgeGraphResponse(BaseModel):
    """知识图谱响应"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class UIElementResponse(BaseModel):
    """UI元素响应"""
    id: str
    name: str
    locators: List[Dict[str, str]]
    last_updated: str
    page: str