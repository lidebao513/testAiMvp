from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import quality

app = FastAPI(
    title="AI Test Engineer Test Quality Scorer",
    description="Service for scoring test case quality based on multiple dimensions",
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
app.include_router(quality.router, prefix="/api/quality", tags=["quality"])

@app.get("/")
async def root():
    return {"message": "AI Test Engineer Test Quality Scorer"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
