import sys
import os

# 添加services/knowledge-service到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services', 'knowledge-service'))

try:
    from app.core.knowledge_base import KnowledgeBase
    print("KnowledgeBase imported successfully!")
    
    # 创建知识库实例
    kb = KnowledgeBase(
        mongo_uri="mongodb://localhost:27017",
        milvus_uri="localhost:19530"
    )
    print("KnowledgeBase instance created successfully!")
    print(f"Milvus connected: {kb.milvus_connected}")
    
    # 测试添加缺陷
    defect = {
        "title": "测试缺陷",
        "description": "这是一个测试缺陷",
        "severity": "High"
    }
    defect_id = kb.add_defect(defect)
    print(f"Defect added successfully with ID: {defect_id}")
    
    # 测试获取缺陷列表
    defects = kb.get_defects()
    print(f"Defects count: {len(defects)}")
    
    print("All tests passed!")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()