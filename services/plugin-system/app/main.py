from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import plugins
from app.core.plugin_loader import PluginLoader
from app.core.plugin_manager import PluginManager
import os

app = FastAPI(
    title="AI Test Engineer Plugin System",
    description="Service for managing test plugins for different platforms and technologies",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(plugins.router, prefix="/api/plugins", tags=["plugins"])

# 初始化插件系统
@app.on_event("startup")
async def startup_event():
    """启动时加载插件"""
    plugins_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")
    loader = PluginLoader(plugins_dir)
    plugin_manager = PluginManager()
    
    # 加载插件
    plugins_list = loader.load_plugins()
    for plugin_data in plugins_list:
        try:
            # 检查插件是否已存在
            existing_plugins = plugin_manager.get_plugins()
            plugin_exists = any(p["name"] == plugin_data["name"] for p in existing_plugins)
            
            if not plugin_exists:
                plugin_manager.create_plugin(plugin_data)
                print(f"Loaded plugin: {plugin_data['name']}")
        except Exception as e:
            print(f"Error loading plugin {plugin_data.get('name', 'unknown')}: {e}")

@app.get("/")
async def root():
    return {"message": "AI Test Engineer Plugin System"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/plugins/count")
async def get_plugins_count():
    """获取插件数量"""
    plugin_manager = PluginManager()
    plugins = plugin_manager.get_plugins()
    return {"count": len(plugins), "plugins": [p["name"] for p in plugins]}
