from fastapi import FastAPI
from app.api.endpoints import generate

app = FastAPI(title="Generator Service", description="AI Test Engineer Generator Service")

app.include_router(generate.router, prefix="/api/generate", tags=["generate"])

@app.get("/")
async def root():
    return {"message": "Generator Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}