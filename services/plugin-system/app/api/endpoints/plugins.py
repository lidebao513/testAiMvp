from fastapi import APIRouter, HTTPException
from app.core.plugin_manager import PluginManager
from app.schemas.plugin import (
    PluginCreate,
    PluginUpdate,
    PluginResponse,
    PluginTemplateCreate,
    PluginTemplateUpdate,
    PluginStrategyCreate,
    PluginStrategyUpdate
)

router = APIRouter()
plugin_manager = PluginManager()

@router.post("/", response_model=PluginResponse)
async def create_plugin(plugin: PluginCreate):
    """创建插件"""
    try:
        result = plugin_manager.create_plugin(plugin.dict())
        return PluginResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[PluginResponse])
async def get_plugins():
    """获取所有插件"""
    try:
        plugins = plugin_manager.get_plugins()
        return [PluginResponse(**plugin) for plugin in plugins]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{plugin_id}", response_model=PluginResponse)
async def get_plugin(plugin_id: str):
    """获取插件详情"""
    try:
        plugin = plugin_manager.get_plugin(plugin_id)
        return PluginResponse(**plugin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{plugin_id}", response_model=PluginResponse)
async def update_plugin(plugin_id: str, plugin: PluginUpdate):
    """更新插件"""
    try:
        result = plugin_manager.update_plugin(plugin_id, plugin.dict())
        return PluginResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{plugin_id}")
async def delete_plugin(plugin_id: str):
    """删除插件"""
    try:
        result = plugin_manager.delete_plugin(plugin_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{plugin_id}/templates")
async def add_template(plugin_id: str, template: PluginTemplateCreate):
    """添加测试模板"""
    try:
        result = plugin_manager.add_template(plugin_id, template.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{plugin_id}/templates")
async def get_templates(plugin_id: str):
    """获取插件的测试模板"""
    try:
        templates = plugin_manager.get_templates(plugin_id)
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{plugin_id}/templates/{template_id}")
async def update_template(plugin_id: str, template_id: str, template: PluginTemplateUpdate):
    """更新测试模板"""
    try:
        result = plugin_manager.update_template(plugin_id, template_id, template.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{plugin_id}/templates/{template_id}")
async def delete_template(plugin_id: str, template_id: str):
    """删除测试模板"""
    try:
        result = plugin_manager.delete_template(plugin_id, template_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{plugin_id}/strategies")
async def add_strategy(plugin_id: str, strategy: PluginStrategyCreate):
    """添加测试策略"""
    try:
        result = plugin_manager.add_strategy(plugin_id, strategy.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{plugin_id}/strategies")
async def get_strategies(plugin_id: str):
    """获取插件的测试策略"""
    try:
        strategies = plugin_manager.get_strategies(plugin_id)
        return {"strategies": strategies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{plugin_id}/strategies/{strategy_id}")
async def update_strategy(plugin_id: str, strategy_id: str, strategy: PluginStrategyUpdate):
    """更新测试策略"""
    try:
        result = plugin_manager.update_strategy(plugin_id, strategy_id, strategy.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{plugin_id}/strategies/{strategy_id}")
async def delete_strategy(plugin_id: str, strategy_id: str):
    """删除测试策略"""
    try:
        result = plugin_manager.delete_strategy(plugin_id, strategy_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category/{category}")
async def get_plugins_by_category(category: str):
    """按分类获取插件"""
    try:
        plugins = plugin_manager.get_plugins_by_category(category)
        return {"plugins": plugins}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
