from fastapi import APIRouter, HTTPException
from app.core.self_healer import SelfHealer
from app.schemas.heal import (
    HealUILocatorRequest,
    HealUILocatorResponse,
    HealApiAssertionRequest,
    HealApiAssertionResponse,
    HealTestDataRequest,
    HealTestDataResponse,
    HealingActionResponse,
    ApproveActionRequest,
    RejectActionRequest,
    ActionResponse,
    KnowledgeGraphResponse,
    UIElementResponse
)

router = APIRouter()
healer = SelfHealer()

@router.post("/heal/ui", response_model=HealUILocatorResponse)
async def heal_ui_locator(request: HealUILocatorRequest):
    """自愈UI元素定位"""
    try:
        new_locator = healer.heal_ui_locator(
            test_id=request.test_id,
            element_name=request.element_name,
            page=request.page,
            current_locator=request.current_locator,
            page_source=request.page_source
        )
        if new_locator:
            return HealUILocatorResponse(
                success=True,
                new_locator=new_locator,
                message="UI元素定位自愈成功"
            )
        else:
            return HealUILocatorResponse(
                success=False,
                new_locator=None,
                message="无法自愈UI元素定位"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/heal/api", response_model=HealApiAssertionResponse)
async def heal_api_assertion(request: HealApiAssertionRequest):
    """自愈API断言"""
    try:
        new_assertion = healer.heal_api_assertion(
            test_id=request.test_id,
            endpoint=request.endpoint,
            original_assertion=request.original_assertion,
            actual_response=request.actual_response
        )
        if new_assertion:
            return HealApiAssertionResponse(
                success=True,
                new_assertion=new_assertion,
                message="API断言自愈成功"
            )
        else:
            return HealApiAssertionResponse(
                success=False,
                new_assertion=None,
                message="无法自愈API断言"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/heal/data", response_model=HealTestDataResponse)
async def heal_test_data(request: HealTestDataRequest):
    """自愈测试数据"""
    try:
        new_data = healer.heal_test_data(
            test_id=request.test_id,
            data_type=request.data_type,
            original_data=request.original_data
        )
        if new_data:
            return HealTestDataResponse(
                success=True,
                new_data=new_data,
                message="测试数据自愈成功"
            )
        else:
            return HealTestDataResponse(
                success=False,
                new_data=None,
                message="无法自愈测试数据"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/actions/pending", response_model=list[HealingActionResponse])
async def get_pending_actions():
    """获取待审核的自愈操作"""
    try:
        pending_actions = healer.get_pending_actions()
        return [
            HealingActionResponse(
                id=action.id,
                type=action.type,
                test_id=action.test_id,
                original_value=action.original_value,
                new_value=action.new_value,
                timestamp=action.timestamp,
                confidence=action.confidence,
                status=action.status
            )
            for action in pending_actions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/actions/approve", response_model=ActionResponse)
async def approve_action(request: ApproveActionRequest):
    """批准自愈操作"""
    try:
        success = healer.approve_action(request.action_id)
        if success:
            return ActionResponse(
                success=True,
                message="自愈操作批准成功"
            )
        else:
            return ActionResponse(
                success=False,
                message="自愈操作不存在"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/actions/reject", response_model=ActionResponse)
async def reject_action(request: RejectActionRequest):
    """拒绝自愈操作"""
    try:
        success = healer.reject_action(request.action_id)
        if success:
            return ActionResponse(
                success=True,
                message="自愈操作拒绝成功"
            )
        else:
            return ActionResponse(
                success=False,
                message="自愈操作不存在"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ui-elements", response_model=list[UIElementResponse])
async def get_ui_elements():
    """获取所有UI元素"""
    try:
        ui_elements = healer.get_ui_elements()
        return [
            UIElementResponse(
                id=elem.id,
                name=elem.name,
                locators=elem.locators,
                last_updated=elem.last_updated,
                page=elem.page
            )
            for elem in ui_elements.values()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-graph", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph():
    """获取知识图谱"""
    try:
        knowledge_graph = healer.get_knowledge_graph()
        return KnowledgeGraphResponse(
            nodes=knowledge_graph["nodes"],
            edges=knowledge_graph["edges"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))