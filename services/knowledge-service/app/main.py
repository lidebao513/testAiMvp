from fastapi import FastAPI
from app.api.endpoints import knowledge

app = FastAPI(title="Knowledge Service", description="AI Test Engineer Knowledge Service")

app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])

@app.get("/")
async def root():
    return {"message": "Knowledge Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}