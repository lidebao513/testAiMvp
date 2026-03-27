import pytest
from app.core.knowledge_base import KnowledgeBase
# import pytest_mock

class TestKnowledgeBase:
    """知识库单元测试类"""

    def setup_method(self):
        """设置测试环境"""
        # 创建知识库实例，使用内存模式（不连接MongoDB和Milvus）
        self.kb = KnowledgeBase(
            mongo_uri="mongodb://localhost:27017",
            milvus_uri="localhost:19530"
        )

    def test_init(self):
        """测试知识库初始化"""
        assert self.kb is not None
        assert self.kb.milvus_connected is False

    def test_add_defect(self):
        """测试添加缺陷"""
        defect = {
            "title": "测试缺陷",
            "description": "这是一个测试缺陷",
            "severity": "High"
        }
        defect_id = self.kb.add_defect(defect)
        assert defect_id is not None
        assert isinstance(defect_id, str)

    def test_get_defects(self):
        """测试获取缺陷列表"""
        # 添加测试缺陷
        defect = {
            "title": "测试缺陷",
            "description": "这是一个测试缺陷",
            "severity": "High"
        }
        self.kb.add_defect(defect)
        
        # 获取缺陷列表
        defects = self.kb.get_defects()
        assert isinstance(defects, list)
        assert len(defects) > 0

    def test_add_test_pattern(self):
        """测试添加测试模式"""
        pattern = {
            "name": "边界值测试",
            "description": "测试边界条件",
            "category": "单元测试"
        }
        pattern_id = self.kb.add_test_pattern(pattern)
        assert pattern_id is not None
        assert isinstance(pattern_id, str)

    def test_get_test_patterns(self):
        """测试获取测试模式列表"""
        # 添加测试模式
        pattern = {
            "name": "边界值测试",
            "description": "测试边界条件",
            "category": "单元测试"
        }
        self.kb.add_test_pattern(pattern)
        
        # 获取测试模式列表
        patterns = self.kb.get_test_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_add_best_practice(self):
        """测试添加最佳实践"""
        practice = {
            "title": "测试命名规范",
            "description": "测试方法名应清晰表达测试目的",
            "category": "测试规范"
        }
        practice_id = self.kb.add_best_practice(practice)
        assert practice_id is not None
        assert isinstance(practice_id, str)

    def test_get_best_practices(self):
        """测试获取最佳实践列表"""
        # 添加最佳实践
        practice = {
            "title": "测试命名规范",
            "description": "测试方法名应清晰表达测试目的",
            "category": "测试规范"
        }
        self.kb.add_best_practice(practice)
        
        # 获取最佳实践列表
        practices = self.kb.get_best_practices()
        assert isinstance(practices, list)
        assert len(practices) > 0

    def test_add_test_case(self):
        """测试添加测试用例"""
        test_case = {
            "title": "登录测试",
            "description": "测试用户登录功能",
            "steps": "1. 打开登录页面\n2. 输入用户名和密码\n3. 点击登录按钮"
        }
        test_case_id = self.kb.add_test_case(test_case)
        assert test_case_id is not None
        assert isinstance(test_case_id, str)

    def test_get_test_cases(self):
        """测试获取测试用例列表"""
        # 添加测试用例
        test_case = {
            "title": "登录测试",
            "description": "测试用户登录功能",
            "steps": "1. 打开登录页面\n2. 输入用户名和密码\n3. 点击登录按钮"
        }
        self.kb.add_test_case(test_case)
        
        # 获取测试用例列表
        test_cases = self.kb.get_test_cases()
        assert isinstance(test_cases, list)
        assert len(test_cases) > 0

    def test_add_defect_pattern(self):
        """测试添加缺陷模式"""
        defect_pattern = {
            "name": "空指针异常",
            "description": "访问空对象导致的异常",
            "symptoms": "系统崩溃"
        }
        defect_pattern_id = self.kb.add_defect_pattern(defect_pattern)
        assert defect_pattern_id is not None
        assert isinstance(defect_pattern_id, str)

    def test_get_defect_patterns(self):
        """测试获取缺陷模式列表"""
        # 添加缺陷模式
        defect_pattern = {
            "name": "空指针异常",
            "description": "访问空对象导致的异常",
            "symptoms": "系统崩溃"
        }
        self.kb.add_defect_pattern(defect_pattern)
        
        # 获取缺陷模式列表
        defect_patterns = self.kb.get_defect_patterns()
        assert isinstance(defect_patterns, list)
        assert len(defect_patterns) > 0

    def test_search_similar(self):
        """测试搜索相似知识"""
        # 由于Milvus未连接，应该返回空列表
        query_embedding = [0.1] * 768  # 模拟768维向量
        similar_items = self.kb.search_similar(query_embedding, top_k=5)
        assert isinstance(similar_items, list)
        assert len(similar_items) == 0

    def test_rag_enhanced_generation(self):
        """测试RAG增强生成"""
        result = self.kb.rag_enhanced_generation("如何测试登录功能")
        assert isinstance(result, dict)
        assert "query" in result
        assert "context" in result
        assert "enhanced_prompt" in result
        assert result["query"] == "如何测试登录功能"
        assert isinstance(result["context"], list)

    def test_generate_embedding_no_model(self):
        """测试未配置嵌入模型时的行为"""
        with pytest.raises(Exception) as excinfo:
            self.kb.generate_embedding("测试文本")
        assert "未配置嵌入模型" in str(excinfo.value)

    def test_search_similar_test_cases(self):
        """测试搜索相似测试用例"""
        # 由于Milvus未连接，应该返回空列表
        similar_test_cases = self.kb.search_similar_test_cases("登录测试", top_k=5)
        assert isinstance(similar_test_cases, list)
        assert len(similar_test_cases) == 0

    def test_search_similar_defects(self):
        """测试搜索相似缺陷"""
        # 由于Milvus未连接，应该返回空列表
        similar_defects = self.kb.search_similar_defects("登录失败", top_k=5)
        assert isinstance(similar_defects, list)
        assert len(similar_defects) == 0
