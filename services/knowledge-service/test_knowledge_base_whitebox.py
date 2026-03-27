import pytest
from app.core.knowledge_base import KnowledgeBase

class TestKnowledgeBaseWhiteBox:
    """知识库白盒测试类"""

    def setup_method(self):
        """设置测试环境"""
        # 创建知识库实例，使用内存模式（不连接MongoDB和Milvus）
        self.kb = KnowledgeBase(
            mongo_uri="mongodb://localhost:27017",
            milvus_uri="localhost:19530"
        )

    def test_add_defect_with_empty_data(self):
        """测试添加空缺陷数据"""
        # 测试添加空缺陷
        defect = {}
        defect_id = self.kb.add_defect(defect)
        assert defect_id is not None
        assert isinstance(defect_id, str)

    def test_add_defect_with_incomplete_data(self):
        """测试添加不完整的缺陷数据"""
        # 测试只添加标题的缺陷
        defect = {"title": "测试缺陷"}
        defect_id = self.kb.add_defect(defect)
        assert defect_id is not None
        assert isinstance(defect_id, str)

    def test_get_defects_with_filter(self):
        """测试带过滤条件获取缺陷列表"""
        # 添加测试缺陷
        defect1 = {"title": "缺陷1", "severity": "High"}
        defect2 = {"title": "缺陷2", "severity": "Medium"}
        self.kb.add_defect(defect1)
        self.kb.add_defect(defect2)
        
        # 测试过滤高严重程度的缺陷
        high_defects = self.kb.get_defects({"severity": "High"})
        assert isinstance(high_defects, list)
        assert len(high_defects) > 0

    def test_add_test_pattern_with_empty_data(self):
        """测试添加空测试模式数据"""
        # 测试添加空测试模式
        pattern = {}
        pattern_id = self.kb.add_test_pattern(pattern)
        assert pattern_id is not None
        assert isinstance(pattern_id, str)

    def test_get_test_patterns_with_filter(self):
        """测试带过滤条件获取测试模式列表"""
        # 添加测试模式
        pattern1 = {"name": "模式1", "category": "单元测试"}
        pattern2 = {"name": "模式2", "category": "集成测试"}
        self.kb.add_test_pattern(pattern1)
        self.kb.add_test_pattern(pattern2)
        
        # 测试过滤单元测试类别
        unit_patterns = self.kb.get_test_patterns({"category": "单元测试"})
        assert isinstance(unit_patterns, list)
        assert len(unit_patterns) > 0

    def test_add_best_practice_with_empty_data(self):
        """测试添加空最佳实践数据"""
        # 测试添加空最佳实践
        practice = {}
        practice_id = self.kb.add_best_practice(practice)
        assert practice_id is not None
        assert isinstance(practice_id, str)

    def test_get_best_practices_with_filter(self):
        """测试带过滤条件获取最佳实践列表"""
        # 添加最佳实践
        practice1 = {"title": "实践1", "category": "测试规范"}
        practice2 = {"title": "实践2", "category": "编码规范"}
        self.kb.add_best_practice(practice1)
        self.kb.add_best_practice(practice2)
        
        # 测试过滤测试规范类别
        test_practices = self.kb.get_best_practices({"category": "测试规范"})
        assert isinstance(test_practices, list)
        assert len(test_practices) > 0

    def test_add_test_case_with_empty_data(self):
        """测试添加空测试用例数据"""
        # 测试添加空测试用例
        test_case = {}
        test_case_id = self.kb.add_test_case(test_case)
        assert test_case_id is not None
        assert isinstance(test_case_id, str)

    def test_get_test_cases_with_filter(self):
        """测试带过滤条件获取测试用例列表"""
        # 添加测试用例
        test_case1 = {"title": "测试用例1", "category": "E2E"}
        test_case2 = {"title": "测试用例2", "category": "单元测试"}
        self.kb.add_test_case(test_case1)
        self.kb.add_test_case(test_case2)
        
        # 测试过滤E2E类别
        e2e_test_cases = self.kb.get_test_cases({"category": "E2E"})
        assert isinstance(e2e_test_cases, list)
        assert len(e2e_test_cases) > 0

    def test_add_defect_pattern_with_empty_data(self):
        """测试添加空缺陷模式数据"""
        # 测试添加空缺陷模式
        defect_pattern = {}
        defect_pattern_id = self.kb.add_defect_pattern(defect_pattern)
        assert defect_pattern_id is not None
        assert isinstance(defect_pattern_id, str)

    def test_get_defect_patterns_with_filter(self):
        """测试带过滤条件获取缺陷模式列表"""
        # 添加缺陷模式
        defect_pattern1 = {"name": "模式1", "category": "性能"}
        defect_pattern2 = {"name": "模式2", "category": "安全"}
        self.kb.add_defect_pattern(defect_pattern1)
        self.kb.add_defect_pattern(defect_pattern2)
        
        # 测试过滤性能类别
        performance_patterns = self.kb.get_defect_patterns({"category": "性能"})
        assert isinstance(performance_patterns, list)
        assert len(performance_patterns) > 0

    def test_rag_enhanced_generation_with_empty_query(self):
        """测试使用空查询进行RAG增强生成"""
        result = self.kb.rag_enhanced_generation("")
        assert isinstance(result, dict)
        assert "query" in result
        assert "context" in result
        assert "enhanced_prompt" in result
        assert result["query"] == ""

    def test_rag_enhanced_generation_with_long_query(self):
        """测试使用长查询进行RAG增强生成"""
        long_query = "如何测试登录功能，包括正常登录、密码错误、账号不存在、验证码错误等场景，以及登录后的权限验证和会话管理"
        result = self.kb.rag_enhanced_generation(long_query)
        assert isinstance(result, dict)
        assert "query" in result
        assert "context" in result
        assert "enhanced_prompt" in result
        assert result["query"] == long_query

    def test_search_similar_with_invalid_embedding(self):
        """测试使用无效的嵌入向量进行相似搜索"""
        # 使用维度不正确的向量
        invalid_embedding = [0.1] * 100  # 应该是768维
        similar_items = self.kb.search_similar(invalid_embedding, top_k=5)
        assert isinstance(similar_items, list)
        assert len(similar_items) == 0

    def test_search_similar_test_cases_with_category_filter(self):
        """测试带类别过滤的相似测试用例搜索"""
        similar_test_cases = self.kb.search_similar_test_cases("登录测试", top_k=5, category="E2E")
        assert isinstance(similar_test_cases, list)
        assert len(similar_test_cases) == 0

    def test_search_similar_defects_with_empty_query(self):
        """测试使用空查询搜索相似缺陷"""
        similar_defects = self.kb.search_similar_defects("", top_k=5)
        assert isinstance(similar_defects, list)
        assert len(similar_defects) == 0
