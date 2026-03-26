import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    
    # 测试添加测试用例
    test_case = {
        "title": "测试用例",
        "description": "这是一个测试用例",
        "steps": "1. 打开页面\n2. 点击按钮\n3. 验证结果"
    }
    test_case_id = kb.add_test_case(test_case)
    print(f"Test case added successfully with ID: {test_case_id}")
    
    # 测试添加缺陷模式
    defect_pattern = {
        "name": "测试缺陷模式",
        "description": "这是一个测试缺陷模式",
        "symptoms": "系统崩溃"
    }
    defect_pattern_id = kb.add_defect_pattern(defect_pattern)
    print(f"Defect pattern added successfully with ID: {defect_pattern_id}")
    
    # 测试获取缺陷列表
    defects = kb.get_defects()
    print(f"Defects count: {len(defects)}")
    
    # 测试获取测试用例列表
    test_cases = kb.get_test_cases()
    print(f"Test cases count: {len(test_cases)}")
    
    # 测试获取缺陷模式列表
    defect_patterns = kb.get_defect_patterns()
    print(f"Defect patterns count: {len(defect_patterns)}")
    
    # 测试RAG增强生成
    rag_result = kb.rag_enhanced_generation("如何测试登录功能")
    print(f"RAG enhanced prompt generated successfully!")
    print(f"Context count: {len(rag_result['context'])}")
    
    print("All tests passed!")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()