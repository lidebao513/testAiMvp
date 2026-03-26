import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler

class ABTestingEngine:
    def __init__(self):
        # 初始化MongoDB连接
        try:
            self.client = MongoClient("mongodb://localhost:27017")
            self.db = self.client["ai_test_engineer"]
            self.strategies_collection = self.db["ab_test_strategies"]
            self.executions_collection = self.db["ab_test_executions"]
            self.reports_collection = self.db["ab_test_reports"]
        except Exception as e:
            print(f"MongoDB连接失败: {e}")
            # 降级到内存存储
            self.strategies = []
            self.executions = []
            self.reports = []
        
        # 预定义的测试策略
        self._initialize_default_strategies()
    
    def _initialize_default_strategies(self):
        """初始化默认测试策略"""
        default_strategies = [
            {
                "name": "traditional",
                "type": "traditional",
                "description": "传统测试策略，基于人工编写的测试用例",
                "parameters": {
                    "test_design_techniques": ["边界值分析", "等价类划分", "判定表"],
                    "coverage_target": 80,
                    "execution_parallelism": 1
                }
            },
            {
                "name": "ai-enhanced",
                "type": "ai-enhanced",
                "description": "AI增强测试策略，使用AI生成测试用例",
                "parameters": {
                    "test_design_techniques": ["边界值分析", "等价类划分", "判定表", "AI路径覆盖"],
                    "coverage_target": 90,
                    "execution_parallelism": 4,
                    "ai_model": "GPT-4"
                }
            },
            {
                "name": "hybrid",
                "type": "hybrid",
                "description": "混合测试策略，结合传统和AI增强方法",
                "parameters": {
                    "test_design_techniques": ["边界值分析", "等价类划分", "判定表", "AI路径覆盖"],
                    "coverage_target": 85,
                    "execution_parallelism": 2,
                    "ai_model": "CodeLlama"
                }
            }
        ]
        
        for strategy in default_strategies:
            try:
                if not self.strategies_collection.find_one({"name": strategy["name"]}):
                    self.strategies_collection.insert_one(strategy)
            except Exception:
                if not any(s["name"] == strategy["name"] for s in self.strategies):
                    self.strategies.append(strategy)
    
    def create_strategy(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建测试策略"""
        strategy = {
            "name": strategy_data["name"],
            "type": strategy_data["type"],
            "description": strategy_data.get("description"),
            "parameters": strategy_data.get("parameters", {}),
            "created_at": datetime.now()
        }
        
        try:
            self.strategies_collection.insert_one(strategy)
        except Exception:
            self.strategies.append(strategy)
        
        return {"message": f"策略 {strategy['name']} 创建成功", "strategy": strategy}
    
    def get_strategies(self) -> List[Dict[str, Any]]:
        """获取所有测试策略"""
        try:
            strategies = list(self.strategies_collection.find())
            for strategy in strategies:
                strategy["_id"] = str(strategy["_id"])
        except Exception:
            strategies = self.strategies
        
        return strategies
    
    def execute_ab_test(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行A/B测试"""
        test_id = str(uuid.uuid4())
        strategies = execution_data["strategies"]
        test_suite = execution_data["test_suite"]
        environment = execution_data.get("environment", "default")
        
        # 执行每个策略并收集结果
        results = []
        for strategy_name in strategies:
            # 模拟测试执行
            result = self._simulate_test_execution(test_id, strategy_name, test_suite, environment)
            results.append(result)
        
        # 保存执行结果
        execution = {
            "test_id": test_id,
            "strategies": strategies,
            "test_suite": test_suite,
            "environment": environment,
            "results": results,
            "executed_at": datetime.now()
        }
        
        try:
            self.executions_collection.insert_one(execution)
        except Exception:
            self.executions.append(execution)
        
        # 生成报告
        report = self.generate_report(test_id)
        
        return {
            "message": "A/B测试执行完成",
            "test_id": test_id,
            "results": results,
            "report": report
        }
    
    def _simulate_test_execution(self, test_id: str, strategy_name: str, test_suite: str, environment: str) -> Dict[str, Any]:
        """模拟测试执行"""
        # 根据策略类型模拟不同的测试结果
        if strategy_name == "traditional":
            # 传统策略：较低的缺陷发现率，较长的执行时间，较高的维护成本
            defect_discovery_rate = np.random.uniform(0.6, 0.75)
            execution_time = np.random.uniform(120, 180)  # 秒
            maintenance_cost = np.random.uniform(80, 120)  # 小时
        elif strategy_name == "ai-enhanced":
            # AI增强策略：较高的缺陷发现率，较短的执行时间，较低的维护成本
            defect_discovery_rate = np.random.uniform(0.8, 0.95)
            execution_time = np.random.uniform(60, 120)  # 秒
            maintenance_cost = np.random.uniform(40, 80)  # 小时
        else:  # hybrid
            # 混合策略：中等的缺陷发现率，中等的执行时间，中等的维护成本
            defect_discovery_rate = np.random.uniform(0.75, 0.85)
            execution_time = np.random.uniform(90, 150)  # 秒
            maintenance_cost = np.random.uniform(60, 100)  # 小时
        
        return {
            "test_id": test_id,
            "strategy_name": strategy_name,
            "defect_discovery_rate": defect_discovery_rate,
            "execution_time": execution_time,
            "maintenance_cost": maintenance_cost,
            "status": "completed",
            "executed_at": datetime.now()
        }
    
    def generate_report(self, test_id: str) -> Dict[str, Any]:
        """生成A/B测试报告"""
        # 获取测试执行结果
        try:
            execution = self.executions_collection.find_one({"test_id": test_id})
        except Exception:
            execution = next((e for e in self.executions if e["test_id"] == test_id), None)
        
        if not execution:
            raise Exception(f"测试执行 {test_id} 不存在")
        
        results = execution["results"]
        strategies = execution["strategies"]
        
        # 计算指标对比
        metrics_comparison = {}
        for strategy_name in strategies:
            result = next((r for r in results if r["strategy_name"] == strategy_name), None)
            if result:
                metrics_comparison[strategy_name] = {
                    "defect_discovery_rate": result["defect_discovery_rate"],
                    "execution_time": result["execution_time"],
                    "maintenance_cost": result["maintenance_cost"]
                }
        
        # 选择最优策略
        best_strategy = self._select_best_strategy(results)
        
        # 生成推荐
        recommendations = self._generate_recommendations(results, best_strategy)
        
        # 创建报告
        report = {
            "report_id": str(uuid.uuid4()),
            "test_id": test_id,
            "generated_at": datetime.now(),
            "strategies": strategies,
            "results": results,
            "best_strategy": best_strategy,
            "metrics_comparison": metrics_comparison,
            "recommendations": recommendations
        }
        
        try:
            self.reports_collection.insert_one(report)
        except Exception:
            self.reports.append(report)
        
        return report
    
    def _select_best_strategy(self, results: List[Dict[str, Any]]) -> str:
        """选择最优策略"""
        # 使用加权评分选择最优策略
        # 权重：缺陷发现率(0.5)，执行时间(0.3)，维护成本(0.2)
        # 执行时间和维护成本越低越好，所以需要取倒数
        best_score = -float('inf')
        best_strategy = ""
        
        for result in results:
            # 归一化指标
            defect_score = result["defect_discovery_rate"]
            time_score = 1 / (result["execution_time"] / 100)  # 归一化到0-1范围
            cost_score = 1 / (result["maintenance_cost"] / 100)  # 归一化到0-1范围
            
            # 计算加权评分
            score = 0.5 * defect_score + 0.3 * time_score + 0.2 * cost_score
            
            if score > best_score:
                best_score = score
                best_strategy = result["strategy_name"]
        
        return best_strategy
    
    def _generate_recommendations(self, results: List[Dict[str, Any]], best_strategy: str) -> List[str]:
        """生成推荐"""
        recommendations = []
        
        # 分析每个策略的表现
        for result in results:
            strategy_name = result["strategy_name"]
            if strategy_name == best_strategy:
                recommendations.append(f"推荐使用 {strategy_name} 策略，在所有指标上表现最优")
            else:
                # 分析该策略的优缺点
                if result["defect_discovery_rate"] > 0.8:
                    recommendations.append(f"{strategy_name} 策略在缺陷发现率方面表现良好，可以考虑与 {best_strategy} 策略结合使用")
                if result["execution_time"] < 100:
                    recommendations.append(f"{strategy_name} 策略执行速度快，适合时间敏感的场景")
                if result["maintenance_cost"] < 70:
                    recommendations.append(f"{strategy_name} 策略维护成本低，适合长期项目")
        
        # 基于整体表现生成推荐
        avg_defect_rate = np.mean([r["defect_discovery_rate"] for r in results])
        avg_execution_time = np.mean([r["execution_time"] for r in results])
        avg_maintenance_cost = np.mean([r["maintenance_cost"] for r in results])
        
        if avg_defect_rate < 0.8:
            recommendations.append("考虑增加AI增强策略的使用比例，提高缺陷发现率")
        if avg_execution_time > 150:
            recommendations.append("优化测试执行流程，减少执行时间")
        if avg_maintenance_cost > 90:
            recommendations.append("考虑使用更自动化的测试策略，降低维护成本")
        
        return recommendations
    
    def get_all_reports(self) -> List[Dict[str, Any]]:
        """获取所有A/B测试报告"""
        try:
            reports = list(self.reports_collection.find())
            for report in reports:
                report["_id"] = str(report["_id"])
        except Exception:
            reports = self.reports
        
        return reports
    
    def get_best_strategy(self) -> Dict[str, Any]:
        """获取最优策略"""
        # 获取所有执行结果
        try:
            executions = list(self.executions_collection.find())
        except Exception:
            executions = self.executions
        
        if not executions:
            return {"message": "没有测试执行数据"}
        
        # 汇总所有策略的表现
        strategy_performance = {}
        for execution in executions:
            for result in execution["results"]:
                strategy_name = result["strategy_name"]
                if strategy_name not in strategy_performance:
                    strategy_performance[strategy_name] = []
                strategy_performance[strategy_name].append(result)
        
        # 计算每个策略的平均表现
        strategy_averages = {}
        for strategy_name, results in strategy_performance.items():
            avg_defect_rate = np.mean([r["defect_discovery_rate"] for r in results])
            avg_execution_time = np.mean([r["execution_time"] for r in results])
            avg_maintenance_cost = np.mean([r["maintenance_cost"] for r in results])
            
            # 计算加权评分
            defect_score = avg_defect_rate
            time_score = 1 / (avg_execution_time / 100)
            cost_score = 1 / (avg_maintenance_cost / 100)
            score = 0.5 * defect_score + 0.3 * time_score + 0.2 * cost_score
            
            strategy_averages[strategy_name] = {
                "average_defect_discovery_rate": avg_defect_rate,
                "average_execution_time": avg_execution_time,
                "average_maintenance_cost": avg_maintenance_cost,
                "score": score
            }
        
        # 选择最优策略
        best_strategy = max(strategy_averages, key=lambda x: strategy_averages[x]["score"])
        best_performance = strategy_averages[best_strategy]
        
        return {
            "best_strategy": best_strategy,
            "performance": best_performance,
            "all_strategies": strategy_averages
        }
    
    def compare_strategies(self) -> Dict[str, Any]:
        """对比策略"""
        # 获取所有执行结果
        try:
            executions = list(self.executions_collection.find())
        except Exception:
            executions = self.executions
        
        if not executions:
            return {"message": "没有测试执行数据"}
        
        # 汇总所有策略的表现
        strategy_performance = {}
        for execution in executions:
            for result in execution["results"]:
                strategy_name = result["strategy_name"]
                if strategy_name not in strategy_performance:
                    strategy_performance[strategy_name] = []
                strategy_performance[strategy_name].append(result)
        
        # 计算每个策略的平均表现
        metrics = {}
        for strategy_name, results in strategy_performance.items():
            avg_defect_rate = np.mean([r["defect_discovery_rate"] for r in results])
            avg_execution_time = np.mean([r["execution_time"] for r in results])
            avg_maintenance_cost = np.mean([r["maintenance_cost"] for r in results])
            
            metrics[strategy_name] = {
                "defect_discovery_rate": avg_defect_rate,
                "execution_time": avg_execution_time,
                "maintenance_cost": avg_maintenance_cost
            }
        
        # 按每个指标选择最优策略
        best_by_metric = {}
        strategies = list(metrics.keys())
        
        # 缺陷发现率：越高越好
        best_by_metric["defect_discovery_rate"] = max(strategies, key=lambda x: metrics[x]["defect_discovery_rate"])
        
        # 执行时间：越低越好
        best_by_metric["execution_time"] = min(strategies, key=lambda x: metrics[x]["execution_time"])
        
        # 维护成本：越低越好
        best_by_metric["maintenance_cost"] = min(strategies, key=lambda x: metrics[x]["maintenance_cost"])
        
        # 计算综合评分
        strategy_scores = {}
        for strategy_name in strategies:
            defect_score = metrics[strategy_name]["defect_discovery_rate"]
            time_score = 1 / (metrics[strategy_name]["execution_time"] / 100)
            cost_score = 1 / (metrics[strategy_name]["maintenance_cost"] / 100)
            score = 0.5 * defect_score + 0.3 * time_score + 0.2 * cost_score
            strategy_scores[strategy_name] = score
        
        overall_best = max(strategy_scores, key=lambda x: strategy_scores[x])
        
        return {
            "strategies": strategies,
            "metrics": metrics,
            "best_by_metric": best_by_metric,
            "overall_best": overall_best
        }
