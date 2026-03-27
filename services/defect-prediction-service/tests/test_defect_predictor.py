import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# 添加父目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.defect_predictor import DefectPredictor, DefectReport
from pathlib import Path

class TestDefectPredictor(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        self.api_key = "test_api_key"
        self.temp_dir = Path("./test_temp")
        self.temp_dir.mkdir(exist_ok=True)
        
        # 创建测试用的DefectPredictor实例
        self.predictor = DefectPredictor(api_key=self.api_key, repo_path=".")
        
        # 保存原始存储路径
        self.original_storage_path = self.predictor.storage_path
        # 设置临时存储路径
        self.predictor.storage_path = self.temp_dir
        self.predictor.defects_file = self.temp_dir / "defects.json"
        self.predictor.code_history_file = self.temp_dir / "code_history.json"
        
        # 清空测试数据
        if self.predictor.defects_file.exists():
            self.predictor.defects_file.unlink()
        if self.predictor.code_history_file.exists():
            self.predictor.code_history_file.unlink()
        
        # 重新加载数据
        self.predictor.defects = self.predictor._load_defects()
        self.predictor.code_history = self.predictor._load_code_history()
    
    def tearDown(self):
        """清理测试环境"""
        # 清理临时文件
        if self.temp_dir.exists():
            # 递归删除目录及其内容
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Error cleaning up test directory: {e}")
    
    def test_initialization(self):
        """测试初始化功能"""
        self.assertEqual(self.predictor.api_key, self.api_key)
        self.assertIsNotNone(self.predictor.risk_model)
        self.assertIsNotNone(self.predictor.gnn_model)
        self.assertEqual(len(self.predictor.defects), 0)
        self.assertEqual(len(self.predictor.code_history["commits"]), 0)
    
    def test_load_defects_empty(self):
        """测试加载空缺陷数据"""
        defects = self.predictor._load_defects()
        self.assertEqual(len(defects), 0)
    
    def test_save_and_load_defects(self):
        """测试保存和加载缺陷数据"""
        # 创建测试缺陷报告
        test_defect = DefectReport(
            id="test_1",
            title="Test Defect",
            description="Test Description",
            root_cause="Test Root Cause",
            severity="High",
            impact=["Module A", "Module B"],
            reproduction_steps=["Step 1", "Step 2"],
            suggested_fix="Test Fix",
            similar_defects=["defect_1", "defect_2"],
            timestamp="2026-03-27T00:00:00"
        )
        
        # 保存缺陷
        self.predictor.defects.append(test_defect)
        self.predictor._save_defects()
        
        # 重新加载
        self.predictor.defects = []
        self.predictor.defects = self.predictor._load_defects()
        
        self.assertEqual(len(self.predictor.defects), 1)
        self.assertEqual(self.predictor.defects[0].id, "test_1")
        self.assertEqual(self.predictor.defects[0].title, "Test Defect")
    
    def test_load_code_history_empty(self):
        """测试加载空代码历史数据"""
        code_history = self.predictor._load_code_history()
        self.assertEqual(len(code_history["commits"]), 0)
        self.assertEqual(len(code_history["file_changes"]), 0)
    
    def test_save_and_load_code_history(self):
        """测试保存和加载代码历史数据"""
        # 创建测试代码历史
        test_history = {
            "commits": [{
                "hash": "test_hash",
                "message": "Test Commit",
                "author": "Test Author",
                "date": "2026-03-27T00:00:00",
                "files_changed": 1
            }],
            "file_changes": {
                "test.py": {
                    "changes": 1,
                    "additions": 10,
                    "deletions": 5,
                    "last_changed": "2026-03-27T00:00:00"
                }
            }
        }
        
        # 保存代码历史
        self.predictor.code_history = test_history
        self.predictor._save_code_history()
        
        # 重新加载
        self.predictor.code_history = {}
        self.predictor.code_history = self.predictor._load_code_history()
        
        self.assertEqual(len(self.predictor.code_history["commits"]), 1)
        self.assertEqual(len(self.predictor.code_history["file_changes"]), 1)
        self.assertEqual(self.predictor.code_history["commits"][0]["hash"], "test_hash")
    
    def test_predict_high_risk_modules(self):
        """测试预测高风险模块"""
        # 创建测试文件变更数据
        file_changes = {
            "high_risk.py": {
                "changes": 25,  # 高变更频率
                "additions": 1500,  # 高变更幅度
                "deletions": 500,
                "last_changed": "2026-03-26T00:00:00"  # 最近变更
            },
            "low_risk.py": {
                "changes": 5,  # 低变更频率
                "additions": 100,  # 低变更幅度
                "deletions": 50,
                "last_changed": "2026-01-01T00:00:00"  # 很久前变更
            }
        }
        
        # 预测高风险模块
        high_risk_modules = self.predictor._predict_high_risk_modules(file_changes)
        
        # 验证结果
        self.assertGreater(len(high_risk_modules), 0)
        self.assertEqual(high_risk_modules[0]["file_path"], "high_risk.py")
        self.assertGreater(high_risk_modules[0]["risk_score"], 0.5)
    
    def test_find_similar_defects(self):
        """测试查找相似缺陷"""
        # 创建测试缺陷报告
        test_defect = DefectReport(
            id="test_1",
            title="Test Defect",
            description="Test Description",
            root_cause="Null pointer exception",
            severity="High",
            impact=["Module A"],
            reproduction_steps=["Step 1"],
            suggested_fix="Test Fix",
            similar_defects=[],
            timestamp="2026-03-27T00:00:00"
        )
        self.predictor.defects.append(test_defect)
        
        # 查找相似缺陷
        similar_defects = self.predictor._find_similar_defects("null pointer")
        
        # 验证结果
        self.assertEqual(len(similar_defects), 1)
        self.assertEqual(similar_defects[0]["id"], "test_1")
    
    @patch('app.core.defect_predictor.openai.ChatCompletion.create')
    def test_analyze_failure_root_cause(self, mock_chat_completion):
        """测试分析失败根因"""
        # 模拟OpenAI响应
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = json.dumps({
            "root_cause": "Null pointer exception",
            "possible_fixes": ["Add null check"],
            "prevention_measures": ["Use optional types"],
            "confidence": 0.9
        })
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_chat_completion.return_value = mock_response
        
        # 测试失败数据
        failure_data = {
            "test_name": "Test Case",
            "error_message": "NullReferenceException: Object reference not set to an instance of an object",
            "stack_trace": "at TestClass.TestMethod() in TestFile.cs:line 10"
        }
        
        # 分析失败根因
        result = self.predictor.analyze_failure_root_cause(failure_data)
        
        # 验证结果
        self.assertEqual(result["root_cause"], "Null pointer exception")
        self.assertEqual(len(result["possible_fixes"]), 1)
        self.assertEqual(result["confidence"], 0.9)
    
    @patch('app.core.defect_predictor.openai.ChatCompletion.create')
    def test_generate_defect_report(self, mock_chat_completion):
        """测试生成缺陷报告"""
        # 模拟OpenAI响应
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = json.dumps({
            "title": "Test Defect",
            "description": "Test Description",
            "root_cause": "Test Root Cause",
            "severity": "High",
            "impact": ["Module A"],
            "reproduction_steps": ["Step 1"],
            "suggested_fix": "Test Fix",
            "similar_defects": []
        })
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_chat_completion.return_value = mock_response
        
        # 测试缺陷数据
        defect_data = {
            "test_name": "Test Case",
            "error_message": "Test Error",
            "stack_trace": "Test Stack Trace"
        }
        
        # 生成缺陷报告
        report = self.predictor.generate_defect_report(defect_data)
        
        # 验证结果
        self.assertIsInstance(report, DefectReport)
        self.assertEqual(report.title, "Test Defect")
        self.assertEqual(report.severity, "High")
    
    def test_build_dependency_graph(self):
        """测试构建依赖图"""
        # 创建测试目录结构
        test_dir = self.temp_dir / "test_code"
        test_dir.mkdir(exist_ok=True)
        
        # 创建测试文件
        file1 = test_dir / "file1.py"
        file1.write_text("import file2\nfrom file3 import function")
        
        file2 = test_dir / "file2.py"
        file2.write_text("")
        
        file3 = test_dir / "file3.py"
        file3.write_text("")
        
        # 构建依赖图
        graph = self.predictor._build_dependency_graph(str(test_dir))
        
        # 验证结果
        self.assertGreater(len(graph.nodes), 0)
    
    def test_analyze_dependency_graph(self):
        """测试分析依赖图"""
        # 创建测试目录结构
        test_dir = self.temp_dir / "test_code"
        test_dir.mkdir(exist_ok=True)
        
        # 创建测试文件
        file1 = test_dir / "file1.py"
        file1.write_text("import file2")
        
        file2 = test_dir / "file2.py"
        file2.write_text("")
        
        # 构建依赖图
        graph = self.predictor._build_dependency_graph(str(test_dir))
        
        # 分析依赖图
        result = self.predictor._analyze_dependency_graph(graph)
        
        # 验证结果
        self.assertIn("centrality", result)
        self.assertIn("depths", result)
        self.assertIn("key_nodes", result)
        self.assertIn("cycles", result)
    
    def test_get_defects(self):
        """测试获取所有缺陷报告"""
        # 创建测试缺陷报告
        test_defect = DefectReport(
            id="test_1",
            title="Test Defect",
            description="Test Description",
            root_cause="Test Root Cause",
            severity="High",
            impact=["Module A"],
            reproduction_steps=["Step 1"],
            suggested_fix="Test Fix",
            similar_defects=[],
            timestamp="2026-03-27T00:00:00"
        )
        self.predictor.defects.append(test_defect)
        
        # 获取缺陷报告
        defects = self.predictor.get_defects()
        
        # 验证结果
        self.assertEqual(len(defects), 1)
        self.assertEqual(defects[0].id, "test_1")
    
    def test_get_code_history(self):
        """测试获取代码历史数据"""
        # 创建测试代码历史
        test_history = {
            "commits": [{
                "hash": "test_hash",
                "message": "Test Commit",
                "author": "Test Author",
                "date": "2026-03-27T00:00:00",
                "files_changed": 1
            }],
            "file_changes": {}
        }
        self.predictor.code_history = test_history
        
        # 获取代码历史
        code_history = self.predictor.get_code_history()
        
        # 验证结果
        self.assertEqual(len(code_history["commits"]), 1)
        self.assertEqual(code_history["commits"][0]["hash"], "test_hash")

if __name__ == '__main__':
    unittest.main()
