from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import data_factory

app = FastAPI(
    title="Test Data Factory Service",
    description="Service for generating and managing test data with dependency analysis and version control",
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
app.include_router(data_factory.router, prefix="/api/data-factory", tags=["data-factory"])

@app.get("/")
async def root():
    return {"message": "Test Data Factory Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}