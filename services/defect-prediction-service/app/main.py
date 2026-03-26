from fastapi import FastAPI
from app.api.endpoints import defect

app = FastAPI(
    title="Intelligent Defect Prediction Service",
    description="AI-powered defect prediction system for code analysis, root cause analysis, and defect reporting",
    version="1.0.0"
)

app.include_router(defect.router, prefix="/api", tags=["defect"])

@app.get("/")
async def root():
    """根路径"""
    return {"message": "Intelligent Defect Prediction Service is running"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}