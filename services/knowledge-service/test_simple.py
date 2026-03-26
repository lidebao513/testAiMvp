import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Starting test...")
    from app.core.knowledge_base import KnowledgeBase
    print("KnowledgeBase imported successfully!")
    
    print("Creating KnowledgeBase instance...")
    # 创建知识库实例，使用内存中的MongoDB和Milvus
    kb = KnowledgeBase(
        mongo_uri="mongodb://localhost:27017",
        milvus_uri="localhost:19530"
    )
    print("KnowledgeBase instance created successfully!")
    print(f"Milvus connected: {kb.milvus_connected}")
    
    print("Test completed successfully!")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()