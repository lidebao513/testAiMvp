import json
import os
from typing import Dict, List, Optional, Any
from app.core.database import get_mongo_client
from bson import ObjectId

class PluginManager:
    def __init__(self):
        self.client = get_mongo_client()
        self.db = self.client['plugin_system']
        self.plugins_collection = self.db['plugins']
    
    def create_plugin(self, plugin_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新插件"""
        result = self.plugins_collection.insert_one(plugin_data)
        plugin = self.plugins_collection.find_one({"_id": result.inserted_id})
        plugin["_id"] = str(plugin["_id"])
        return plugin
    
    def get_plugins(self) -> List[Dict[str, Any]]:
        """获取所有插件"""
        plugins = []
        for plugin in self.plugins_collection.find():
            plugin["_id"] = str(plugin["_id"])
            plugins.append(plugin)
        return plugins
    
    def get_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """根据ID获取插件"""
        plugin = self.plugins_collection.find_one({"_id": ObjectId(plugin_id)})
        if not plugin:
            raise Exception("Plugin not found")
        plugin["_id"] = str(plugin["_id"])
        return plugin
    
    def update_plugin(self, plugin_id: str, plugin_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新插件"""
        result = self.plugins_collection.update_one(
            {"_id": ObjectId(plugin_id)},
            {"$set": plugin_data}
        )
        if result.modified_count == 0:
            raise Exception("Plugin not found or no changes made")
        return self.get_plugin(plugin_id)
    
    def delete_plugin(self, plugin_id: str) -> Dict[str, str]:
        """删除插件"""
        result = self.plugins_collection.delete_one({"_id": ObjectId(plugin_id)})
        if result.deleted_count == 0:
            raise Exception("Plugin not found")
        return {"message": "Plugin deleted successfully"}
    
    def add_template(self, plugin_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """添加测试模板"""
        result = self.plugins_collection.update_one(
            {"_id": ObjectId(plugin_id)},
            {"$push": {"templates": template_data}}
        )
        if result.modified_count == 0:
            raise Exception("Plugin not found")
        return {"message": "Template added successfully"}
    
    def get_templates(self, plugin_id: str) -> List[Dict[str, Any]]:
        """获取插件的测试模板"""
        plugin = self.get_plugin(plugin_id)
        return plugin.get("templates", [])
    
    def update_template(self, plugin_id: str, template_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新测试模板"""
        result = self.plugins_collection.update_one(
            {"_id": ObjectId(plugin_id), "templates.id": template_id},
            {"$set": {"templates.$": template_data}}
        )
        if result.modified_count == 0:
            raise Exception("Template not found")
        return {"message": "Template updated successfully"}
    
    def delete_template(self, plugin_id: str, template_id: str) -> Dict[str, Any]:
        """删除测试模板"""
        result = self.plugins_collection.update_one(
            {"_id": ObjectId(plugin_id)},
            {"$pull": {"templates": {"id": template_id}}}
        )
        if result.modified_count == 0:
            raise Exception("Template not found")
        return {"message": "Template deleted successfully"}
    
    def add_strategy(self, plugin_id: str, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """添加测试策略"""
        result = self.plugins_collection.update_one(
            {"_id": ObjectId(plugin_id)},
            {"$push": {"strategies": strategy_data}}
        )
        if result.modified_count == 0:
            raise Exception("Plugin not found")
        return {"message": "Strategy added successfully"}
    
    def get_strategies(self, plugin_id: str) -> List[Dict[str, Any]]:
        """获取插件的测试策略"""
        plugin = self.get_plugin(plugin_id)
        return plugin.get("strategies", [])
    
    def update_strategy(self, plugin_id: str, strategy_id: str, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新测试策略"""
        result = self.plugins_collection.update_one(
            {"_id": ObjectId(plugin_id), "strategies.id": strategy_id},
            {"$set": {"strategies.$": strategy_data}}
        )
        if result.modified_count == 0:
            raise Exception("Strategy not found")
        return {"message": "Strategy updated successfully"}
    
    def delete_strategy(self, plugin_id: str, strategy_id: str) -> Dict[str, Any]:
        """删除测试策略"""
        result = self.plugins_collection.update_one(
            {"_id": ObjectId(plugin_id)},
            {"$pull": {"strategies": {"id": strategy_id}}}
        )
        if result.modified_count == 0:
            raise Exception("Strategy not found")
        return {"message": "Strategy deleted successfully"}
    
    def get_plugins_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按分类获取插件"""
        plugins = []
        for plugin in self.plugins_collection.find({"category": category}):
            plugin["_id"] = str(plugin["_id"])
            plugins.append(plugin)
        return plugins