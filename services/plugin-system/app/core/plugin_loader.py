import os
import json
from typing import Dict, List, Any

class PluginLoader:
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
    
    def load_plugins(self) -> List[Dict[str, Any]]:
        """从文件系统加载插件"""
        plugins = []
        if not os.path.exists(self.plugins_dir):
            return plugins
        
        for plugin_dir in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, plugin_dir)
            if not os.path.isdir(plugin_path):
                continue
            
            manifest_path = os.path.join(plugin_path, "manifest.json")
            if not os.path.exists(manifest_path):
                continue
            
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    plugin_data = json.load(f)
                    plugins.append(plugin_data)
            except Exception as e:
                print(f"Error loading plugin {plugin_dir}: {e}")
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """加载指定的插件"""
        plugin_path = os.path.join(self.plugins_dir, plugin_name)
        manifest_path = os.path.join(plugin_path, "manifest.json")
        
        if not os.path.exists(manifest_path):
            raise Exception(f"Plugin {plugin_name} not found")
        
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                plugin_data = json.load(f)
                return plugin_data
        except Exception as e:
            raise Exception(f"Error loading plugin {plugin_name}: {e}")