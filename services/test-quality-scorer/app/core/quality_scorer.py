import json
import os
import uuid
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import spacy
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from pymongo import MongoClient

class QualityScorer:
    def __init__(self):
        # 初始化MongoDB连接
        try:
            self.client = MongoClient("mongodb://localhost:27017")
            self.db = self.client["ai_test_engineer"]
            self.training_data_collection = self.db["quality_training_data"]
            self.scores_collection = self.db["quality_scores"]
        except Exception as e:
            print(f"MongoDB连接失败: {e}")
            # 降级到内存存储
            self.training_data = []
            self.scores = []
        
        # 初始化NLP工具
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"加载Spacy模型失败: {e}")
            self.nlp = None
        
        # 初始化模型
        self.models = {
            "readability": None,
            "completeness": None,
            "independence": None,
            "effectiveness": None
        }
        
        # 初始化特征提取器
        self.feature_extractor = FeatureExtractor()
        
        # 尝试加载已训练的模型
        self._load_models()
    
    def score_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """评估测试用例质量"""
        test_case_id = test_case.get("id", str(uuid.uuid4()))
        content = test_case.get("content", "")
        test_type = test_case.get("type", "unit")
        language = test_case.get("language", "python")
        
        # 提取特征
        features = self.feature_extractor.extract_features(content, test_type, language)
        
        # 计算各维度得分
        readability_score = self._score_readability(content, language)
        completeness_score = self._score_completeness(content, test_type)
        independence_score = self._score_independence(content)
        effectiveness_score = self._score_effectiveness(content, test_type)
        
        # 如果模型已训练，使用模型预测
        if all(model is not None for model in self.models.values()):
            # 使用模型预测
            readability_score = self.models["readability"].predict([features])[0]
            completeness_score = self.models["completeness"].predict([features])[0]
            independence_score = self.models["independence"].predict([features])[0]
            effectiveness_score = self.models["effectiveness"].predict([features])[0]
        
        # 计算总分
        overall_score = (readability_score * 0.25 + 
                        completeness_score * 0.30 + 
                        independence_score * 0.20 + 
                        effectiveness_score * 0.25)
        
        # 生成反馈
        feedback = self._generate_feedback(
            readability_score, 
            completeness_score, 
            independence_score, 
            effectiveness_score,
            content
        )
        
        score_data = {
            "test_case_id": test_case_id,
            "overall_score": overall_score,
            "readability": readability_score,
            "completeness": completeness_score,
            "independence": independence_score,
            "effectiveness": effectiveness_score,
            "feedback": feedback,
            "scored_at": datetime.now()
        }
        
        # 保存评分结果
        try:
            self.scores_collection.insert_one(score_data)
        except Exception:
            self.scores.append(score_data)
        
        return score_data
    
    def _score_readability(self, content: str, language: str) -> float:
        """评估可读性"""
        # 检查命名规范
        good_naming = self._check_naming_conventions(content, language)
        
        # 检查注释比例
        comment_ratio = self._calculate_comment_ratio(content, language)
        
        # 检查代码复杂度
        complexity = self._calculate_code_complexity(content)
        
        # 计算可读性得分
        readability_score = (
            good_naming * 0.4 +
            comment_ratio * 0.3 +
            (1 - complexity) * 0.3
        ) * 100
        
        return readability_score
    
    def _score_completeness(self, content: str, test_type: str) -> float:
        """评估完整性"""
        # 检查断言数量
        assertion_count = self._count_assertions(content, test_type)
        
        # 检查测试步骤完整性
        step_completeness = self._check_step_completeness(content, test_type)
        
        # 检查异常处理
        exception_handling = self._check_exception_handling(content)
        
        # 计算完整性得分
        completeness_score = (
            min(assertion_count / 3, 1) * 0.4 +
            step_completeness * 0.4 +
            exception_handling * 0.2
        ) * 100
        
        return completeness_score
    
    def _score_independence(self, content: str) -> float:
        """评估独立性"""
        # 检查外部依赖
        external_dependencies = self._check_external_dependencies(content)
        
        # 检查测试间依赖
        inter_test_dependencies = self._check_inter_test_dependencies(content)
        
        # 计算独立性得分
        independence_score = (
            (1 - external_dependencies) * 0.6 +
            (1 - inter_test_dependencies) * 0.4
        ) * 100
        
        return independence_score
    
    def _score_effectiveness(self, content: str, test_type: str) -> float:
        """评估有效性"""
        # 检查边界条件测试
        boundary_tests = self._check_boundary_tests(content)
        
        # 检查错误场景测试
        error_scenario_tests = self._check_error_scenario_tests(content)
        
        # 检查业务逻辑测试
        business_logic_tests = self._check_business_logic_tests(content, test_type)
        
        # 计算有效性得分
        effectiveness_score = (
            boundary_tests * 0.3 +
            error_scenario_tests * 0.3 +
            business_logic_tests * 0.4
        ) * 100
        
        return effectiveness_score
    
    def _check_naming_conventions(self, content: str, language: str) -> float:
        """检查命名规范"""
        # 简单的命名规范检查
        # 对于Python，检查蛇形命名法
        if language == "python":
            # 检查函数和变量命名
            function_pattern = r"def\s+([a-zA-Z0-9_]+)\s*\("
            variable_pattern = r"([a-zA-Z0-9_]+)\s*="
            
            functions = re.findall(function_pattern, content)
            variables = re.findall(variable_pattern, content)
            
            # 检查蛇形命名法
            snake_case_functions = [f for f in functions if re.match(r"^[a-z_][a-z0-9_]*$", f)]
            snake_case_variables = [v for v in variables if re.match(r"^[a-z_][a-z0-9_]*$", v)]
            
            if functions:
                function_score = len(snake_case_functions) / len(functions)
            else:
                function_score = 1.0
            
            if variables:
                variable_score = len(snake_case_variables) / len(variables)
            else:
                variable_score = 1.0
            
            return (function_score + variable_score) / 2
        
        # 对于JavaScript，检查驼峰命名法
        elif language == "javascript":
            # 检查函数和变量命名
            function_pattern = r"function\s+([a-zA-Z0-9_]+)\s*\("
            variable_pattern = r"([a-zA-Z0-9_]+)\s*="
            
            functions = re.findall(function_pattern, content)
            variables = re.findall(variable_pattern, content)
            
            # 检查驼峰命名法
            camel_case_functions = [f for f in functions if re.match(r"^[A-Z][a-z0-9]*([A-Z][a-z0-9]*)*$", f)]
            camel_case_variables = [v for v in variables if re.match(r"^[a-z][a-z0-9]*([A-Z][a-z0-9]*)*$", v)]
            
            if functions:
                function_score = len(camel_case_functions) / len(functions)
            else:
                function_score = 1.0
            
            if variables:
                variable_score = len(camel_case_variables) / len(variables)
            else:
                variable_score = 1.0
            
            return (function_score + variable_score) / 2
        
        return 0.8  # 默认得分
    
    def _calculate_comment_ratio(self, content: str, language: str) -> float:
        """计算注释比例"""
        # 简单的注释比例计算
        lines = content.split('\n')
        total_lines = len(lines)
        comment_lines = 0
        
        for line in lines:
            line = line.strip()
            if language == "python" and line.startswith('#'):
                comment_lines += 1
            elif language == "javascript" and (line.startswith('//') or line.startswith('/*') or line.endswith('*/')):
                comment_lines += 1
            elif language == "java" and (line.startswith('//') or line.startswith('/*') or line.endswith('*/')):
                comment_lines += 1
        
        if total_lines > 0:
            return min(comment_lines / total_lines * 5, 1.0)  # 注释比例不超过20%
        return 0.0
    
    def _calculate_code_complexity(self, content: str) -> float:
        """计算代码复杂度"""
        # 简单的代码复杂度计算
        # 计算控制流语句数量
        control_flow_patterns = [
            r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b', r'\bswitch\b',
            r'\btry\b', r'\bcatch\b', r'\bfinally\b'
        ]
        
        complexity = 0
        for pattern in control_flow_patterns:
            complexity += len(re.findall(pattern, content))
        
        # 归一化复杂度
        return min(complexity / 10, 1.0)  # 最大复杂度为10
    
    def _count_assertions(self, content: str, test_type: str) -> int:
        """计算断言数量"""
        # 不同测试类型的断言模式
        assertion_patterns = []
        
        if test_type == "unit":
            assertion_patterns = [
                r'\bassert\b', r'\bexpect\b', r'\bshould\b',
                r'\bassertEqual\b', r'\bassertTrue\b', r'\bassertFalse\b'
            ]
        elif test_type == "api":
            assertion_patterns = [
                r'\bassert\b', r'\bexpect\b', r'\bshould\b',
                r'\bstatusCode\b', r'\btoEqual\b', r'\btoContain\b'
            ]
        elif test_type == "e2e":
            assertion_patterns = [
                r'\bassert\b', r'\bexpect\b', r'\bshould\b',
                r'\btoHaveText\b', r'\btoHaveAttribute\b', r'\btoBeVisible\b'
            ]
        
        assertion_count = 0
        for pattern in assertion_patterns:
            assertion_count += len(re.findall(pattern, content))
        
        return assertion_count
    
    def _check_step_completeness(self, content: str, test_type: str) -> float:
        """检查测试步骤完整性"""
        # 检查测试步骤的完整性
        # 对于单元测试，检查Arrange-Act-Assert模式
        if test_type == "unit":
            # 简单检查是否包含arrange、act、assert等关键词
            arrange_patterns = [r'\barrange\b', r'\bsetup\b', r'\bprepare\b']
            act_patterns = [r'\bact\b', r'\bexecute\b', r'\bcall\b']
            assert_patterns = [r'\bassert\b', r'\bverify\b', r'\bcheck\b']
            
            has_arrange = any(len(re.findall(pattern, content, re.IGNORECASE)) > 0 for pattern in arrange_patterns)
            has_act = any(len(re.findall(pattern, content, re.IGNORECASE)) > 0 for pattern in act_patterns)
            has_assert = any(len(re.findall(pattern, content, re.IGNORECASE)) > 0 for pattern in assert_patterns)
            
            steps = [has_arrange, has_act, has_assert]
            return sum(steps) / len(steps)
        
        # 对于API测试，检查请求和响应验证
        elif test_type == "api":
            # 检查是否包含请求和响应验证
            request_patterns = [r'\brequest\b', r'\bget\b', r'\bpost\b', r'\bput\b', r'\bdelete\b']
            response_patterns = [r'\bresponse\b', r'\bstatus\b', r'\bdata\b']
            
            has_request = any(len(re.findall(pattern, content, re.IGNORECASE)) > 0 for pattern in request_patterns)
            has_response = any(len(re.findall(pattern, content, re.IGNORECASE)) > 0 for pattern in response_patterns)
            
            steps = [has_request, has_response]
            return sum(steps) / len(steps)
        
        # 对于E2E测试，检查页面交互和验证
        elif test_type == "e2e":
            # 检查是否包含页面交互和验证
            interaction_patterns = [r'\bclick\b', r'\bfill\b', r'\bnavigate\b', r'\bselect\b']
            verification_patterns = [r'\bexpect\b', r'\bassert\b', r'\bverify\b']
            
            has_interaction = any(len(re.findall(pattern, content, re.IGNORECASE)) > 0 for pattern in interaction_patterns)
            has_verification = any(len(re.findall(pattern, content, re.IGNORECASE)) > 0 for pattern in verification_patterns)
            
            steps = [has_interaction, has_verification]
            return sum(steps) / len(steps)
        
        return 0.5  # 默认得分
    
    def _check_exception_handling(self, content: str) -> float:
        """检查异常处理"""
        # 检查是否包含异常处理
        exception_patterns = [
            r'\btry\b', r'\bcatch\b', r'\bfinally\b',
            r'\bexcept\b', r'\bthrow\b', r'\bassertThrows\b'
        ]
        
        has_exception_handling = any(len(re.findall(pattern, content)) > 0 for pattern in exception_patterns)
        return 1.0 if has_exception_handling else 0.5
    
    def _check_external_dependencies(self, content: str) -> float:
        """检查外部依赖"""
        # 检查是否包含外部依赖
        external_dependencies = [
            r'\brequire\b', r'\bimport\b', r'\bfrom\b',
            r'\bdependency\b', r'\bexternal\b', r'\bapi\b'
        ]
        
        dependency_count = 0
        for pattern in external_dependencies:
            dependency_count += len(re.findall(pattern, content, re.IGNORECASE))
        
        # 归一化依赖数量
        return min(dependency_count / 5, 1.0)  # 最大依赖数量为5
    
    def _check_inter_test_dependencies(self, content: str) -> float:
        """检查测试间依赖"""
        # 检查是否包含测试间依赖
        inter_test_patterns = [
            r'\btest\d+\b', r'\bsetup\b', r'\bteardown\b',
            r'\bbeforeEach\b', r'\bafterEach\b', r'\bshared\b'
        ]
        
        dependency_count = 0
        for pattern in inter_test_patterns:
            dependency_count += len(re.findall(pattern, content, re.IGNORECASE))
        
        # 归一化依赖数量
        return min(dependency_count / 3, 1.0)  # 最大依赖数量为3
    
    def _check_boundary_tests(self, content: str) -> float:
        """检查边界条件测试"""
        # 检查是否包含边界条件测试
        boundary_patterns = [
            r'\bmax\b', r'\bmin\b', r'\b边界\b',
            r'\b边界值\b', r'\b极限\b', r'\b边界条件\b',
            r'\b0\b', r'\b1\b', r'\b-1\b',
            r'\bnull\b', r'\bundefined\b', r'\bempty\b'
        ]
        
        boundary_count = 0
        for pattern in boundary_patterns:
            boundary_count += len(re.findall(pattern, content, re.IGNORECASE))
        
        # 归一化边界条件数量
        return min(boundary_count / 3, 1.0)  # 最大边界条件数量为3
    
    def _check_error_scenario_tests(self, content: str) -> float:
        """检查错误场景测试"""
        # 检查是否包含错误场景测试
        error_patterns = [
            r'\berror\b', r'\bfail\b', r'\bexception\b',
            r'\b错误\b', r'\b异常\b', r'\b失败\b',
            r'\bthrow\b', r'\bassertThrows\b', r'\bshouldThrow\b'
        ]
        
        error_count = 0
        for pattern in error_patterns:
            error_count += len(re.findall(pattern, content, re.IGNORECASE))
        
        # 归一化错误场景数量
        return min(error_count / 2, 1.0)  # 最大错误场景数量为2
    
    def _check_business_logic_tests(self, content: str, test_type: str) -> float:
        """检查业务逻辑测试"""
        # 检查是否包含业务逻辑测试
        business_patterns = [
            r'\b业务\b', r'\blogic\b', r'\b流程\b',
            r'\b功能\b', r'\bfeature\b', r'\bscenario\b'
        ]
        
        business_count = 0
        for pattern in business_patterns:
            business_count += len(re.findall(pattern, content, re.IGNORECASE))
        
        # 归一化业务逻辑测试数量
        return min(business_count / 2, 1.0)  # 最大业务逻辑测试数量为2
    
    def _generate_feedback(self, readability: float, completeness: float, independence: float, effectiveness: float, content: str) -> List[str]:
        """生成反馈"""
        feedback = []
        
        if readability < 70:
            feedback.append("可读性需要改进：建议使用更清晰的命名规范，增加注释说明")
        
        if completeness < 70:
            feedback.append("完整性需要改进：建议增加更多的断言，确保测试步骤完整")
        
        if independence < 70:
            feedback.append("独立性需要改进：建议减少外部依赖，确保测试用例之间相互独立")
        
        if effectiveness < 70:
            feedback.append("有效性需要改进：建议增加边界条件测试和错误场景测试")
        
        if all(score >= 80 for score in [readability, completeness, independence, effectiveness]):
            feedback.append("测试用例质量优秀，各项指标表现良好")
        
        return feedback
    
    def add_training_data(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """添加训练数据"""
        training_data["created_at"] = datetime.now()
        
        try:
            self.training_data_collection.insert_one(training_data)
        except Exception:
            self.training_data.append(training_data)
        
        return {"message": "训练数据添加成功", "training_data": training_data}
    
    def train_model(self, training_request: Dict[str, Any]) -> Dict[str, Any]:
        """训练质量评分模型"""
        # 收集训练数据
        try:
            training_data = list(self.training_data_collection.find())
        except Exception:
            training_data = self.training_data
        
        if len(training_data) < 10:
            return {"message": "训练数据不足，需要至少10条训练数据"}
        
        # 准备训练数据
        X = []
        y_readability = []
        y_completeness = []
        y_independence = []
        y_effectiveness = []
        
        for data in training_data:
            test_case = data["test_case"]
            content = test_case.get("content", "")
            test_type = test_case.get("type", "unit")
            language = test_case.get("language", "python")
            
            # 提取特征
            features = self.feature_extractor.extract_features(content, test_type, language)
            X.append(features)
            
            # 添加标签
            y_readability.append(data["readability_score"])
            y_completeness.append(data["completeness_score"])
            y_independence.append(data["independence_score"])
            y_effectiveness.append(data["effectiveness_score"])
        
        # 分割数据
        test_size = training_request.get("test_size", 0.2)
        X_train, X_test, y_readability_train, y_readability_test = train_test_split(X, y_readability, test_size=test_size, random_state=42)
        _, _, y_completeness_train, y_completeness_test = train_test_split(X, y_completeness, test_size=test_size, random_state=42)
        _, _, y_independence_train, y_independence_test = train_test_split(X, y_independence, test_size=test_size, random_state=42)
        _, _, y_effectiveness_train, y_effectiveness_test = train_test_split(X, y_effectiveness, test_size=test_size, random_state=42)
        
        # 选择模型类型
        model_type = training_request.get("model_type", "random_forest")
        
        # 训练模型
        models = {}
        metrics = {}
        
        # 训练可读性模型
        if model_type == "random_forest":
            models["readability"] = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == "svm":
            models["readability"] = SVR(kernel="rbf")
        
        models["readability"].fit(X_train, y_readability_train)
        y_readability_pred = models["readability"].predict(X_test)
        metrics["readability"] = {
            "mse": mean_squared_error(y_readability_test, y_readability_pred),
            "r2": r2_score(y_readability_test, y_readability_pred)
        }
        
        # 训练完整性模型
        if model_type == "random_forest":
            models["completeness"] = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == "svm":
            models["completeness"] = SVR(kernel="rbf")
        
        models["completeness"].fit(X_train, y_completeness_train)
        y_completeness_pred = models["completeness"].predict(X_test)
        metrics["completeness"] = {
            "mse": mean_squared_error(y_completeness_test, y_completeness_pred),
            "r2": r2_score(y_completeness_test, y_completeness_pred)
        }
        
        # 训练独立性模型
        if model_type == "random_forest":
            models["independence"] = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == "svm":
            models["independence"] = SVR(kernel="rbf")
        
        models["independence"].fit(X_train, y_independence_train)
        y_independence_pred = models["independence"].predict(X_test)
        metrics["independence"] = {
            "mse": mean_squared_error(y_independence_test, y_independence_pred),
            "r2": r2_score(y_independence_test, y_independence_pred)
        }
        
        # 训练有效性模型
        if model_type == "random_forest":
            models["effectiveness"] = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == "svm":
            models["effectiveness"] = SVR(kernel="rbf")
        
        models["effectiveness"].fit(X_train, y_effectiveness_train)
        y_effectiveness_pred = models["effectiveness"].predict(X_test)
        metrics["effectiveness"] = {
            "mse": mean_squared_error(y_effectiveness_test, y_effectiveness_pred),
            "r2": r2_score(y_effectiveness_test, y_effectiveness_pred)
        }
        
        # 保存模型
        self.models = models
        
        return {
            "message": "模型训练完成",
            "metrics": metrics,
            "model_type": model_type,
            "training_samples": len(training_data)
        }
    
    def get_model_status(self) -> Dict[str, Any]:
        """获取模型状态"""
        model_status = {}
        for model_name, model in self.models.items():
            model_status[model_name] = "trained" if model is not None else "not_trained"
        
        return {
            "model_status": model_status,
            "last_updated": datetime.now()
        }
    
    def get_quality_stats(self) -> Dict[str, Any]:
        """获取质量统计信息"""
        try:
            scores = list(self.scores_collection.find())
        except Exception:
            scores = self.scores
        
        if not scores:
            return {"message": "没有评分数据"}
        
        # 计算统计信息
        overall_scores = [s["overall_score"] for s in scores]
        readability_scores = [s["readability"] for s in scores]
        completeness_scores = [s["completeness"] for s in scores]
        independence_scores = [s["independence"] for s in scores]
        effectiveness_scores = [s["effectiveness"] for s in scores]
        
        stats = {
            "total_test_cases": len(scores),
            "average_overall_score": np.mean(overall_scores),
            "average_readability": np.mean(readability_scores),
            "average_completeness": np.mean(completeness_scores),
            "average_independence": np.mean(independence_scores),
            "average_effectiveness": np.mean(effectiveness_scores),
            "min_overall_score": np.min(overall_scores),
            "max_overall_score": np.max(overall_scores),
            "last_updated": datetime.now()
        }
        
        return stats
    
    def _load_models(self):
        """加载已训练的模型"""
        # 这里可以实现模型的加载逻辑
        # 目前使用内存存储，所以不需要加载
        pass

class FeatureExtractor:
    def __init__(self):
        # 初始化特征提取器
        pass
    
    def extract_features(self, content: str, test_type: str, language: str) -> List[float]:
        """提取测试用例的特征"""
        features = []
        
        # 1. 代码长度特征
        line_count = len(content.split('\n'))
        char_count = len(content)
        word_count = len(content.split())
        features.extend([line_count, char_count, word_count])
        
        # 2. 注释特征
        comment_ratio = self._calculate_comment_ratio(content, language)
        features.append(comment_ratio)
        
        # 3. 代码复杂度特征
        complexity = self._calculate_code_complexity(content)
        features.append(complexity)
        
        # 4. 断言数量特征
        assertion_count = self._count_assertions(content, test_type)
        features.append(assertion_count)
        
        # 5. 控制流特征
        control_flow_count = self._count_control_flow(content)
        features.append(control_flow_count)
        
        # 6. 异常处理特征
        exception_handling = self._has_exception_handling(content)
        features.append(1 if exception_handling else 0)
        
        # 7. 外部依赖特征
        external_dependencies = self._count_external_dependencies(content)
        features.append(external_dependencies)
        
        # 8. 测试类型特征
        test_type_features = self._get_test_type_features(test_type)
        features.extend(test_type_features)
        
        # 9. 语言特征
        language_features = self._get_language_features(language)
        features.extend(language_features)
        
        return features
    
    def _calculate_comment_ratio(self, content: str, language: str) -> float:
        """计算注释比例"""
        lines = content.split('\n')
        total_lines = len(lines)
        comment_lines = 0
        
        for line in lines:
            line = line.strip()
            if language == "python" and line.startswith('#'):
                comment_lines += 1
            elif language == "javascript" and (line.startswith('//') or line.startswith('/*') or line.endswith('*/')):
                comment_lines += 1
            elif language == "java" and (line.startswith('//') or line.startswith('/*') or line.endswith('*/')):
                comment_lines += 1
        
        if total_lines > 0:
            return comment_lines / total_lines
        return 0.0
    
    def _calculate_code_complexity(self, content: str) -> float:
        """计算代码复杂度"""
        control_flow_patterns = [
            r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b', r'\bswitch\b',
            r'\btry\b', r'\bcatch\b', r'\bfinally\b'
        ]
        
        complexity = 0
        for pattern in control_flow_patterns:
            complexity += len(re.findall(pattern, content))
        
        return complexity
    
    def _count_assertions(self, content: str, test_type: str) -> int:
        """计算断言数量"""
        assertion_patterns = []
        
        if test_type == "unit":
            assertion_patterns = [
                r'\bassert\b', r'\bexpect\b', r'\bshould\b',
                r'\bassertEqual\b', r'\bassertTrue\b', r'\bassertFalse\b'
            ]
        elif test_type == "api":
            assertion_patterns = [
                r'\bassert\b', r'\bexpect\b', r'\bshould\b',
                r'\bstatusCode\b', r'\btoEqual\b', r'\btoContain\b'
            ]
        elif test_type == "e2e":
            assertion_patterns = [
                r'\bassert\b', r'\bexpect\b', r'\bshould\b',
                r'\btoHaveText\b', r'\btoHaveAttribute\b', r'\btoBeVisible\b'
            ]
        
        assertion_count = 0
        for pattern in assertion_patterns:
            assertion_count += len(re.findall(pattern, content))
        
        return assertion_count
    
    def _count_control_flow(self, content: str) -> int:
        """计算控制流语句数量"""
        control_flow_patterns = [
            r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b', r'\bswitch\b',
            r'\btry\b', r'\bcatch\b', r'\bfinally\b'
        ]
        
        count = 0
        for pattern in control_flow_patterns:
            count += len(re.findall(pattern, content))
        
        return count
    
    def _has_exception_handling(self, content: str) -> bool:
        """检查是否有异常处理"""
        exception_patterns = [
            r'\btry\b', r'\bcatch\b', r'\bfinally\b',
            r'\bexcept\b', r'\bthrow\b', r'\bassertThrows\b'
        ]
        
        return any(len(re.findall(pattern, content)) > 0 for pattern in exception_patterns)
    
    def _count_external_dependencies(self, content: str) -> int:
        """计算外部依赖数量"""
        external_dependencies = [
            r'\brequire\b', r'\bimport\b', r'\bfrom\b',
            r'\bdependency\b', r'\bexternal\b', r'\bapi\b'
        ]
        
        count = 0
        for pattern in external_dependencies:
            count += len(re.findall(pattern, content, re.IGNORECASE))
        
        return count
    
    def _get_test_type_features(self, test_type: str) -> List[float]:
        """获取测试类型特征"""
        # 独热编码测试类型
        if test_type == "unit":
            return [1, 0, 0]
        elif test_type == "api":
            return [0, 1, 0]
        elif test_type == "e2e":
            return [0, 0, 1]
        else:
            return [0, 0, 0]
    
    def _get_language_features(self, language: str) -> List[float]:
        """获取语言特征"""
        # 独热编码语言
        if language == "python":
            return [1, 0, 0, 0]
        elif language == "javascript":
            return [0, 1, 0, 0]
        elif language == "java":
            return [0, 0, 1, 0]
        else:
            return [0, 0, 0, 1]
