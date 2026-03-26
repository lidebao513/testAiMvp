from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import evolution

app = FastAPI(
    title="AI Test Engineer Self Evolution Service",
    description="Service for AI Test Engineer self evolution and model improvement",
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
app.include_router(evolution.router, prefix="/api/evolution", tags=["evolution"])

@app.get("/")
async def root():
    return {"message": "AI Test Engineer Self Evolution Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
