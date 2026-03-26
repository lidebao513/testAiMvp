from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import ab_testing

app = FastAPI(
    title="AI Test Engineer A/B Testing Service",
    description="Service for A/B testing different test strategies",
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
app.include_router(ab_testing.router, prefix="/api/ab-testing", tags=["ab-testing"])

@app.get("/")
async def root():
    return {"message": "AI Test Engineer A/B Testing Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
