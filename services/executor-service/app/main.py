from fastapi import FastAPI
from app.api.endpoints import execute

app = FastAPI(title="Executor Service", description="AI Test Engineer Executor Service")

app.include_router(execute.router, prefix="/api/execute", tags=["execute"])

@app.get("/")
async def root():
    return {"message": "Executor Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}