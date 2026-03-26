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
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

class SelfEvolutionEngine:
    def __init__(self):
        # 初始化MongoDB连接
        try:
            self.client = MongoClient("mongodb://localhost:27017")
            self.db = self.client["ai_test_engineer"]
            self.feedback_collection = self.db["feedback"]
            self.execution_collection = self.db["execution_results"]
            self.model_metrics_collection = self.db["model_metrics"]
            self.generation_strategies_collection = self.db["generation_strategies"]
        except Exception as e:
            print(f"MongoDB连接失败: {e}")
            # 降级到内存存储
            self.feedback_data = []
            self.execution_data = []
            self.model_metrics = []
            self.generation_strategies = []
        
        # 初始化强化学习参数
        self.alpha = 0.1  # 学习率
        self.gamma = 0.9  # 折扣因子
        self.epsilon = 0.1  # 探索率
        
        # 生成策略
        self.generation_strategies = {
            "basic": {"weight": 0.5, "success_rate": 0.7},
            "advanced": {"weight": 0.3, "success_rate": 0.8},
            "comprehensive": {"weight": 0.2, "success_rate": 0.85}
        }
    
    def add_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """添加人工审核反馈"""
        feedback_id = str(uuid.uuid4())
        feedback_data = {
            "id": feedback_id,
            "test_case_id": feedback["test_case_id"],
            "quality_score": feedback["quality_score"],
            "comments": feedback.get("comments"),
            "reviewer": feedback.get("reviewer"),
            "created_at": datetime.now()
        }
        
        try:
            self.feedback_collection.insert_one(feedback_data)
        except Exception:
            self.feedback_data.append(feedback_data)
        
        return feedback_data
    
    def add_execution_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """添加测试执行结果"""
        result_id = str(uuid.uuid4())
        execution_data = {
            "id": result_id,
            "test_case_id": result["test_case_id"],
            "status": result["status"],
            "is_real_defect": result["is_real_defect"],
            "defect_details": result.get("defect_details"),
            "execution_time": result["execution_time"],
            "created_at": datetime.now()
        }
        
        try:
            self.execution_collection.insert_one(execution_data)
        except Exception:
            self.execution_data.append(execution_data)
        
        # 根据执行结果更新生成策略
        self.update_generation_strategy_based_on_execution(execution_data)
        
        return execution_data
    
    def fine_tune_model(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """微调模型"""
        # 收集训练数据
        training_data = self._collect_training_data(request["dataset_size"])
        
        if not training_data:
            return {"message": "训练数据不足"}
        
        # 模拟模型微调
        model_name = request["model_name"]
        epochs = request["epochs"]
        learning_rate = request["learning_rate"]
        
        # 计算模型性能指标
        metrics = self._calculate_model_metrics(training_data)
        
        # 保存模型指标
        model_metric = {
            "model_name": model_name,
            "version": f"{model_name}_v{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "training_date": datetime.now(),
            "metrics": metrics,
            "parameters": {
                "epochs": epochs,
                "learning_rate": learning_rate,
                "dataset_size": len(training_data)
            }
        }
        
        try:
            self.model_metrics_collection.insert_one(model_metric)
        except Exception:
            self.model_metrics.append(model_metric)
        
        return {
            "message": f"模型 {model_name} 微调完成",
            "model_version": model_metric["version"],
            "metrics": metrics
        }
    
    def generate_evolution_report(self) -> Dict[str, Any]:
        """生成进化报告"""
        report_id = str(uuid.uuid4())
        
        # 获取反馈统计
        feedback_stats = self.get_feedback_stats()
        
        # 获取执行统计
        execution_stats = self.get_execution_stats()
        
        # 获取模型指标
        try:
            latest_model = self.model_metrics_collection.find().sort("training_date", -1).limit(1).next()
            previous_model = self.model_metrics_collection.find().sort("training_date", -1).skip(1).limit(1).next()
        except Exception:
            latest_model = self.model_metrics[-1] if self.model_metrics else None
            previous_model = self.model_metrics[-2] if len(self.model_metrics) > 1 else None
        
        # 计算改进
        improvements = []
        metrics = {}
        
        if latest_model and previous_model:
            latest_metrics = latest_model["metrics"]
            previous_metrics = previous_model["metrics"]
            
            for key in latest_metrics:
                if key in previous_metrics:
                    metrics[key] = latest_metrics[key]
                    improvement = (latest_metrics[key] - previous_metrics[key]) / previous_metrics[key] * 100
                    if improvement > 0:
                        improvements.append(f"{key} 提升了 {improvement:.2f}%")
                    elif improvement < 0:
                        improvements.append(f"{key} 下降了 {abs(improvement):.2f}%")
        elif latest_model:
            metrics = latest_model["metrics"]
            improvements.append("首次生成模型，无历史数据对比")
        
        # 生成推荐
        recommendations = self._generate_recommendations(feedback_stats, execution_stats)
        
        report = {
            "report_id": report_id,
            "generated_at": datetime.now(),
            "model_version": latest_model["version"] if latest_model else "N/A",
            "previous_version": previous_model["version"] if previous_model else "N/A",
            "metrics": metrics,
            "improvements": improvements,
            "recommendations": recommendations,
            "feedback_summary": feedback_stats,
            "execution_summary": execution_stats
        }
        
        return report
    
    def optimize_generation_strategy(self) -> Dict[str, Any]:
        """优化生成策略"""
        # 基于强化学习优化生成策略
        self._perform_reinforcement_learning()
        
        # 保存优化后的策略
        try:
            self.generation_strategies_collection.insert_one({
                "timestamp": datetime.now(),
                "strategies": self.generation_strategies
            })
        except Exception:
            self.generation_strategies.append({
                "timestamp": datetime.now(),
                "strategies": self.generation_strategies
            })
        
        return {
            "message": "生成策略优化完成",
            "strategies": self.generation_strategies
        }
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """获取反馈统计信息"""
        try:
            feedbacks = list(self.feedback_collection.find())
        except Exception:
            feedbacks = self.feedback_data
        
        if not feedbacks:
            return {"total_feedbacks": 0, "average_score": 0}
        
        scores = [f["quality_score"] for f in feedbacks]
        average_score = sum(scores) / len(scores)
        
        # 按评分分布
        score_distribution = {}
        for score in range(1, 6):
            score_distribution[f"score_{score}"] = scores.count(score)
        
        return {
            "total_feedbacks": len(feedbacks),
            "average_score": average_score,
            "score_distribution": score_distribution
        }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """获取执行统计信息"""
        try:
            executions = list(self.execution_collection.find())
        except Exception:
            executions = self.execution_data
        
        if not executions:
            return {"total_executions": 0, "success_rate": 0, "real_defect_rate": 0}
        
        success_count = sum(1 for e in executions if e["status"] == "success")
        real_defect_count = sum(1 for e in executions if e["is_real_defect"])
        
        return {
            "total_executions": len(executions),
            "success_rate": success_count / len(executions),
            "real_defect_rate": real_defect_count / len(executions),
            "average_execution_time": sum(e["execution_time"] for e in executions) / len(executions)
        }
    
    def update_generation_strategy_based_on_execution(self, execution_data: Dict[str, Any]):
        """根据执行结果更新生成策略"""
        # 简单的策略更新逻辑
        status = execution_data["status"]
        is_real_defect = execution_data["is_real_defect"]
        
        # 基于执行结果调整策略权重
        if status == "success":
            # 成功执行，增加当前策略的权重
            for strategy in self.generation_strategies:
                self.generation_strategies[strategy]["weight"] *= 1.05
        elif is_real_defect:
            # 发现真实缺陷，增加comprehensive策略的权重
            self.generation_strategies["comprehensive"]["weight"] *= 1.1
        else:
            # 误报，调整策略
            self.generation_strategies["basic"]["weight"] *= 0.95
        
        # 归一化权重
        total_weight = sum(s["weight"] for s in self.generation_strategies.values())
        for strategy in self.generation_strategies:
            self.generation_strategies[strategy]["weight"] /= total_weight
    
    def _collect_training_data(self, dataset_size: int) -> List[Dict[str, Any]]:
        """收集训练数据"""
        try:
            feedbacks = list(self.feedback_collection.find().limit(dataset_size))
            executions = list(self.execution_collection.find().limit(dataset_size))
        except Exception:
            feedbacks = self.feedback_data[:dataset_size]
            executions = self.execution_data[:dataset_size]
        
        # 合并数据
        training_data = []
        for feedback in feedbacks:
            # 查找对应的执行结果
            execution = next((e for e in executions if e["test_case_id"] == feedback["test_case_id"]), None)
            if execution:
                training_data.append({
                    "test_case_id": feedback["test_case_id"],
                    "quality_score": feedback["quality_score"],
                    "status": execution["status"],
                    "is_real_defect": execution["is_real_defect"],
                    "execution_time": execution["execution_time"]
                })
        
        return training_data
    
    def _calculate_model_metrics(self, training_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算模型性能指标"""
        if len(training_data) < 10:
            return {"accuracy": 0.5, "precision": 0.5, "recall": 0.5, "f1": 0.5}
        
        # 准备特征和标签
        X = []
        y = []
        
        for data in training_data:
            features = [
                data["quality_score"],
                data["execution_time"]
            ]
            label = 1 if data["status"] == "success" else 0
            X.append(features)
            y.append(label)
        
        # 分割数据
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 训练模型
        model = LogisticRegression()
        model.fit(X_train, y_train)
        
        # 预测
        y_pred = model.predict(X_test)
        
        # 计算指标
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        return {
            "accuracy": accuracy,
            "precision": report["1"]["precision"],
            "recall": report["1"]["recall"],
            "f1": report["1"]["f1-score"]
        }
    
    def _generate_recommendations(self, feedback_stats: Dict[str, Any], execution_stats: Dict[str, Any]) -> List[str]:
        """生成推荐"""
        recommendations = []
        
        # 基于反馈统计生成推荐
        if feedback_stats.get("average_score", 0) < 3.5:
            recommendations.append("提高测试用例生成质量，重点关注用户反馈的低评分用例")
        
        # 基于执行统计生成推荐
        if execution_stats.get("success_rate", 0) < 0.7:
            recommendations.append("优化测试执行环境，减少执行失败率")
        
        if execution_stats.get("real_defect_rate", 0) < 0.2:
            recommendations.append("增加测试用例的覆盖范围，提高缺陷检测能力")
        
        if execution_stats.get("average_execution_time", 0) > 5:
            recommendations.append("优化测试执行速度，减少执行时间")
        
        # 基于生成策略生成推荐
        comprehensive_weight = self.generation_strategies.get("comprehensive", {}).get("weight", 0)
        if comprehensive_weight < 0.3:
            recommendations.append("增加comprehensive策略的权重，提高测试用例的全面性")
        
        return recommendations
    
    def _perform_reinforcement_learning(self):
        """执行强化学习"""
        # 简单的Q-learning实现
        # 状态空间：当前策略分布
        # 动作空间：调整策略权重
        # 奖励函数：基于测试执行结果和反馈评分
        
        # 模拟强化学习过程
        for _ in range(100):  # 训练回合
            # 随机选择一个策略进行调整
            strategies = list(self.generation_strategies.keys())
            action = np.random.choice(strategies)
            
            # 执行动作（调整权重）
            old_weight = self.generation_strategies[action]["weight"]
            self.generation_strategies[action]["weight"] *= (1 + np.random.uniform(-0.1, 0.1))
            
            # 计算奖励
            feedback_stats = self.get_feedback_stats()
            execution_stats = self.get_execution_stats()
            
            reward = 0
            reward += feedback_stats.get("average_score", 0) * 0.5
            reward += execution_stats.get("success_rate", 0) * 0.3
            reward += execution_stats.get("real_defect_rate", 0) * 0.2
            
            # 更新策略权重
            self.generation_strategies[action]["weight"] = old_weight + self.alpha * reward
            
            # 归一化权重
            total_weight = sum(s["weight"] for s in self.generation_strategies.values())
            for strategy in self.generation_strategies:
                self.generation_strategies[strategy]["weight"] /= total_weight
