from fastapi import FastAPI
from app.api.endpoints import parse

app = FastAPI(title="Parser Service", description="AI Test Engineer Parser Service")

app.include_router(parse.router, prefix="/api/parse", tags=["parse"])

@app.get("/")
async def root():
    return {"message": "Parser Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}