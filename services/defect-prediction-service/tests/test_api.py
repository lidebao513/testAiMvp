import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# 添加父目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.defect_predictor import DefectPredictor, DefectReport

class TestDefectAPI(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        self.client = TestClient(app)
        self.api_key = "test_api_key"
    
    @patch('app.api.endpoints.defect.defect_predictor')
    def test_analyze_code_changes(self, mock_predictor):
        """测试分析代码变更接口"""
        # 模拟预测器响应
        mock_predictor.analyze_code_changes.return_value = {
            "high_risk_modules": [{
                "file_path": "test.py",
                "risk_score": 0.8,
                "changes": 10,
                "total_changes": 100,
                "last_changed": "2026-03-27T00:00:00"
            }],
            "total_commits_analyzed": 10,
            "total_files_analyzed": 5
        }
        
        # 发送请求
        response = self.client.post("/api/analyze/code-changes", json={
            "repo_path": "."
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("high_risk_modules", data)
        self.assertEqual(len(data["high_risk_modules"]), 1)
    
    @patch('app.api.endpoints.defect.defect_predictor')
    def test_analyze_failure(self, mock_predictor):
        """测试分析失败根因接口"""
        # 模拟预测器响应
        mock_predictor.analyze_failure_root_cause.return_value = {
            "root_cause": "Null pointer exception",
            "possible_fixes": ["Add null check"],
            "prevention_measures": ["Use optional types"],
            "confidence": 0.9,
            "similar_defects": []
        }
        
        # 发送请求
        response = self.client.post("/api/analyze/root-cause", json={
            "test_name": "Test Case",
            "error": "NullReferenceException",
            "stack_trace": "Test Stack Trace"
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["root_cause"], "Null pointer exception")
    
    @patch('app.api.endpoints.defect.defect_predictor')
    def test_generate_report(self, mock_predictor):
        """测试生成缺陷报告接口"""
        # 模拟预测器响应
        mock_predictor.generate_defect_report.return_value = DefectReport(
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
        
        # 发送请求
        response = self.client.post("/api/generate/report", json={
            "test_name": "Test Case",
            "error_message": "Test Error",
            "stack_trace": "Test Stack Trace"
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Test Defect")
        self.assertEqual(data["severity"], "High")
    
    @patch('app.api.endpoints.defect.defect_predictor')
    def test_analyze_dependencies(self, mock_predictor):
        """测试分析代码依赖接口"""
        # 模拟预测器响应
        mock_predictor.analyze_code_dependencies.return_value = {
            "dependency_graph": {
                "centrality": {},
                "depths": {},
                "key_nodes": [],
                "cycles": []
            },
            "node_count": 5,
            "edge_count": 3
        }
        
        # 发送请求
        response = self.client.post("/api/analyze/dependencies", json={
            "code_path": "."
        })
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("dependency_graph", data)
        self.assertEqual(data["node_count"], 5)
    
    @patch('app.api.endpoints.defect.defect_predictor')
    def test_get_defects(self, mock_predictor):
        """测试获取缺陷列表接口"""
        # 模拟预测器响应
        mock_predictor.get_defects.return_value = [
            DefectReport(
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
        ]
        
        # 发送请求
        response = self.client.get("/api/defects")
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("defects", data)
        self.assertEqual(len(data["defects"]), 1)
        self.assertEqual(data["defects"][0]["title"], "Test Defect")

if __name__ == '__main__':
    unittest.main()
