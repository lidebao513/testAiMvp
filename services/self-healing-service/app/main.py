from fastapi import FastAPI
from app.api.endpoints import heal

app = FastAPI(
    title="Test Self-Healing Service",
    description="AI-powered test self-healing service for UI elements, API assertions, and test data",
    version="1.0.0"
)

app.include_router(heal.router, prefix="/api", tags=["healing"])

@app.get("/")
async def root():
    """根路径"""
    return {"message": "Test Self-Healing Service is running"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}