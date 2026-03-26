from fastapi import FastAPI
from app.api.endpoints import analyze

app = FastAPI(title="Analytics Service", description="AI Test Engineer Analytics Service")

app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])

@app.get("/")
async def root():
    return {"message": "Analytics Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}