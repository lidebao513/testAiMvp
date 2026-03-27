import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# 添加父目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.defect_predictor import DefectPredictor, DefectReport
from pathlib import Path

class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        self.api_key = "test_api_key"
        
        # 清理数据文件
        storage_path = Path("./defect_prediction_data")
        if storage_path.exists():
            import shutil
            try:
                shutil.rmtree(storage_path)
            except Exception as e:
                print(f"Error cleaning up storage directory: {e}")
        
        self.predictor = DefectPredictor(api_key=self.api_key)
        
        # 创建临时目录用于测试
        self.temp_dir = Path("./test_temp_edge")
        self.temp_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """清理测试环境"""
        # 清理临时文件
        if self.temp_dir.exists():
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Error cleaning up test directory: {e}")
    
    def test_load_code_history_empty(self):
        """测试加载空代码历史数据"""
        # 测试加载不存在的代码历史文件
        result = self.predictor._load_code_history()
        self.assertEqual(result, {"commits": [], "file_changes": {}})
    
    def test_load_defects_empty(self):
        """测试加载空缺陷数据"""
        # 测试加载不存在的缺陷文件
        result = self.predictor._load_defects()
        self.assertEqual(result, [])
    
    @patch('app.core.defect_predictor.openai.ChatCompletion.create')
    def test_analyze_failure_root_cause_error(self, mock_chat_completion):
        """测试分析失败根因时的错误处理"""
        # 模拟OpenAI API错误
        mock_chat_completion.side_effect = Exception("API Error")
        
        # 测试失败数据
        failure_data = {
            "test_name": "Test Case",
            "error": "NullReferenceException",
            "stack_trace": "Test Stack Trace"
        }
        
        # 分析失败根因
        result = self.predictor.analyze_failure_root_cause(failure_data)
        
        # 验证结果
        self.assertEqual(result["root_cause"], "Unknown")
        self.assertEqual(len(result["possible_fixes"]), 0)
        self.assertEqual(result["confidence"], 0.0)
        self.assertIn("error", result)
    
    def test_analyze_code_dependencies_empty(self):
        """测试分析空代码依赖"""
        # 测试分析空目录
        result = self.predictor.analyze_code_dependencies(code_path=str(self.temp_dir))
        
        # 验证结果
        self.assertIn("dependency_graph", result)
        self.assertEqual(result["node_count"], 0)
        self.assertEqual(result["edge_count"], 0)
    
    def test_build_dependency_graph(self):
        """测试构建依赖图"""
        # 创建测试目录结构
        test_dir = self.temp_dir / "test_project"
        test_dir.mkdir(exist_ok=True)
        
        # 创建测试文件
        (test_dir / "__init__.py").write_text("")
        (test_dir / "module1.py").write_text("import module2\n")
        (test_dir / "module2.py").write_text("")
        
        # 构建依赖图
        graph = self.predictor._build_dependency_graph(str(test_dir))
        
        # 验证结果
        self.assertIsNotNone(graph)
    
    def test_analyze_dependency_graph(self):
        """测试分析依赖图"""
        # 创建测试目录结构
        test_dir = self.temp_dir / "test_project"
        test_dir.mkdir(exist_ok=True)
        
        # 创建测试文件
        (test_dir / "__init__.py").write_text("")
        (test_dir / "module1.py").write_text("import module2\n")
        (test_dir / "module2.py").write_text("")
        
        # 构建依赖图
        graph = self.predictor._build_dependency_graph(str(test_dir))
        
        # 分析依赖图
        analysis = self.predictor._analyze_dependency_graph(graph)
        
        # 验证结果
        self.assertIsInstance(analysis, dict)
        self.assertIn("centrality", analysis)
        self.assertIn("depths", analysis)
        self.assertIn("key_nodes", analysis)
        self.assertIn("cycles", analysis)
    
    def test_save_code_history(self):
        """测试保存代码历史数据"""
        # 测试保存代码历史
        code_history = {
            "commits": [{"hash": "test_hash", "message": "Test commit"}],
            "file_changes": {"test.py": {"additions": 10, "deletions": 5}}
        }
        
        # 保存代码历史
        self.predictor.code_history = code_history
        self.predictor._save_code_history()
        
        # 验证保存成功
        loaded_history = self.predictor._load_code_history()
        self.assertEqual(len(loaded_history["commits"]), 1)
    
    def test_save_defects(self):
        """测试保存缺陷数据"""
        # 测试保存缺陷
        defect = DefectReport(
            id="defect_1",
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
        
        # 保存缺陷
        self.predictor.defects = [defect]
        self.predictor._save_defects()
        
        # 验证保存成功
        loaded_defects = self.predictor._load_defects()
        self.assertEqual(len(loaded_defects), 1)
    
    def test_get_code_history(self):
        """测试获取代码历史数据"""
        # 测试获取代码历史
        code_history = {
            "commits": [{"hash": "test_hash", "message": "Test commit"}],
            "file_changes": {"test.py": {"additions": 10, "deletions": 5}}
        }
        
        # 设置代码历史
        self.predictor.code_history = code_history
        
        # 获取代码历史
        result = self.predictor.get_code_history()
        
        # 验证结果
        self.assertEqual(len(result["commits"]), 1)
        self.assertIn("test.py", result["file_changes"])

if __name__ == '__main__':
    unittest.main()
