from typing import List, Dict, Any, Optional
import os
import json
import time
import logging
import datetime
import re
import git
import numpy as np
import pandas as pd
import networkx as nx
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical
import openai
from pathlib import Path
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DefectPredictor")

@dataclass
class DefectReport:
    """缺陷报告类"""
    id: str
    title: str
    description: str
    root_cause: str
    severity: str
    impact: List[str]
    reproduction_steps: List[str]
    suggested_fix: str
    similar_defects: List[str]
    timestamp: str

class DefectPredictor:
    """智能缺陷预测系统"""
    
    def __init__(self, api_key: str, repo_path: str = "."):
        """初始化缺陷预测器
        
        Args:
            api_key (str): OpenAI API密钥
            repo_path (str, optional): 代码仓库路径，默认为"."
        """
        self.api_key = api_key
        openai.api_key = api_key
        self.repo_path = repo_path
        self.repo = None
        
        # 初始化存储路径
        self.storage_path = Path("./defect_prediction_data")
        self.storage_path.mkdir(exist_ok=True)
        
        # 初始化存储文件
        self.defects_file = self.storage_path / "defects.json"
        self.code_history_file = self.storage_path / "code_history.json"
        
        # 加载数据
        self.defects = self._load_defects()
        self.code_history = self._load_code_history()
        
        # 初始化模型
        self.risk_model = None
        self.gnn_model = None
        self._initialize_models()
    
    def _load_defects(self) -> List[DefectReport]:
        """加载缺陷数据"""
        if self.defects_file.exists():
            with open(self.defects_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                defects = []
                for defect_data in data:
                    defects.append(DefectReport(
                        id=defect_data["id"],
                        title=defect_data["title"],
                        description=defect_data["description"],
                        root_cause=defect_data["root_cause"],
                        severity=defect_data["severity"],
                        impact=defect_data["impact"],
                        reproduction_steps=defect_data["reproduction_steps"],
                        suggested_fix=defect_data["suggested_fix"],
                        similar_defects=defect_data["similar_defects"],
                        timestamp=defect_data["timestamp"]
                    ))
                return defects
        return []
    
    def _load_code_history(self) -> Dict[str, Any]:
        """加载代码历史数据"""
        if self.code_history_file.exists():
            with open(self.code_history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"commits": [], "file_changes": {}}
    
    def _save_defects(self):
        """保存缺陷数据"""
        data = []
        for defect in self.defects:
            data.append({
                "id": defect.id,
                "title": defect.title,
                "description": defect.description,
                "root_cause": defect.root_cause,
                "severity": defect.severity,
                "impact": defect.impact,
                "reproduction_steps": defect.reproduction_steps,
                "suggested_fix": defect.suggested_fix,
                "similar_defects": defect.similar_defects,
                "timestamp": defect.timestamp
            })
        with open(self.defects_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_code_history(self):
        """保存代码历史数据"""
        with open(self.code_history_file, "w", encoding="utf-8") as f:
            json.dump(self.code_history, f, ensure_ascii=False, indent=2)
    
    def _initialize_models(self):
        """初始化预测模型"""
        # 初始化风险预测模型
        self.risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # 初始化图神经网络模型（简化版）
        self.gnn_model = Sequential([
            Dense(64, activation='relu', input_shape=(10,)),  # 假设输入特征维度为10
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(2, activation='softmax')  # 二分类：高风险/低风险
        ])
        self.gnn_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    def analyze_code_changes(self, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """分析代码变更历史，预测高风险模块
        
        Args:
            repo_path (Optional[str], optional): 代码仓库路径，默认为None
            
        Returns:
            Dict[str, Any]: 高风险模块分析结果
        """
        logger.info("分析代码变更历史")
        
        if repo_path:
            self.repo_path = repo_path
        
        try:
            # 尝试打开git仓库
            self.repo = git.Repo(self.repo_path)
            
            # 收集最近的提交历史
            commits = []
            for commit in self.repo.iter_commits('HEAD', max_count=100):
                commits.append({
                    "hash": commit.hexsha,
                    "message": commit.message,
                    "author": commit.author.name,
                    "date": commit.committed_datetime.isoformat(),
                    "files_changed": len(commit.stats.files)
                })
            
            # 分析文件变更频率
            file_changes = {}
            for commit in self.repo.iter_commits('HEAD', max_count=200):
                for file_path, stats in commit.stats.files.items():
                    if file_path not in file_changes:
                        file_changes[file_path] = {
                            "changes": 0,
                            "additions": 0,
                            "deletions": 0,
                            "last_changed": commit.committed_datetime.isoformat()
                        }
                    file_changes[file_path]["changes"] += 1
                    file_changes[file_path]["additions"] += stats.get('insertions', 0)
                    file_changes[file_path]["deletions"] += stats.get('deletions', 0)
                    file_changes[file_path]["last_changed"] = commit.committed_datetime.isoformat()
            
            # 更新代码历史数据
            self.code_history = {
                "commits": commits,
                "file_changes": file_changes
            }
            self._save_code_history()
            
            # 预测高风险模块
            high_risk_modules = self._predict_high_risk_modules(file_changes)
            
            return {
                "high_risk_modules": high_risk_modules,
                "total_commits_analyzed": len(commits),
                "total_files_analyzed": len(file_changes)
            }
            
        except Exception as e:
            logger.error(f"分析代码变更历史失败: {str(e)}")
            return {
                "high_risk_modules": [],
                "error": str(e)
            }
    
    def _predict_high_risk_modules(self, file_changes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """预测高风险模块"""
        high_risk_modules = []
        
        for file_path, stats in file_changes.items():
            # 基于变更频率和幅度计算风险分数
            risk_score = 0
            
            # 变更频率权重
            if stats["changes"] > 20:
                risk_score += 0.4
            elif stats["changes"] > 10:
                risk_score += 0.2
            
            # 变更幅度权重
            total_changes = stats["additions"] + stats["deletions"]
            if total_changes > 1000:
                risk_score += 0.3
            elif total_changes > 500:
                risk_score += 0.15
            
            # 最近变更权重
            last_changed = datetime.datetime.fromisoformat(stats["last_changed"])
            days_since_change = (datetime.datetime.now() - last_changed).days
            if days_since_change < 7:
                risk_score += 0.3
            elif days_since_change < 30:
                risk_score += 0.1
            
            # 文件名风险权重
            risky_extensions = [".py", ".js", ".ts", ".java"]
            if any(ext in file_path for ext in risky_extensions):
                risk_score += 0.2
            
            if risk_score > 0.5:
                high_risk_modules.append({
                    "file_path": file_path,
                    "risk_score": round(risk_score, 2),
                    "changes": stats["changes"],
                    "total_changes": total_changes,
                    "last_changed": stats["last_changed"]
                })
        
        # 按风险分数排序
        high_risk_modules.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return high_risk_modules[:10]  # 返回前10个高风险模块
    
    def analyze_failure_root_cause(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """测试失败时自动分析根因
        
        Args:
            failure_data (Dict[str, Any]): 测试失败数据
            
        Returns:
            Dict[str, Any]: 根因分析结果
        """
        logger.info("分析测试失败根因")
        
        # 构建提示词，指导AI模型分析失败根因
        prompt = f"""Analyze the following test failure data and identify the root cause:

{failure_data}

Provide:
1. Root cause analysis (code change, environment, or test itself)
2. Possible fixes
3. Prevention measures
4. Confidence score (0-1)

Format the output as a JSON object."""
        
        try:
            # 调用OpenAI API分析失败根因
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a QA engineer analyzing test failures."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 解析响应
            analysis = json.loads(response.choices[0].message.content)
            
            # 关联历史相似缺陷
            similar_defects = self._find_similar_defects(analysis["root_cause"])
            analysis["similar_defects"] = similar_defects
            
            return analysis
            
        except Exception as e:
            logger.error(f"分析失败根因失败: {str(e)}")
            return {
                "root_cause": "Unknown",
                "possible_fixes": [],
                "prevention_measures": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _find_similar_defects(self, root_cause: str) -> List[str]:
        """查找相似的历史缺陷"""
        similar_defects = []
        
        # 简单的文本匹配策略
        for defect in self.defects:
            if root_cause.lower() in defect.root_cause.lower() or \
               any(keyword in defect.root_cause.lower() for keyword in root_cause.lower().split()):
                similar_defects.append({
                    "id": defect.id,
                    "title": defect.title,
                    "root_cause": defect.root_cause
                })
        
        return similar_defects[:3]  # 返回前3个相似缺陷
    
    def generate_defect_report(self, defect_data: Dict[str, Any]) -> DefectReport:
        """生成缺陷报告
        
        Args:
            defect_data (Dict[str, Any]): 缺陷数据
            
        Returns:
            DefectReport: 缺陷报告
        """
        logger.info("生成缺陷报告")
        
        # 生成缺陷ID
        defect_id = f"defect_{int(time.time())}"
        
        # 构建提示词，指导AI模型生成缺陷报告
        prompt = f"""Generate a comprehensive defect report based on the following data:

{defect_data}

The report should include:
1. Title
2. Detailed description
3. Root cause analysis
4. Severity (High/Medium/Low)
5. Impact scope
6. Reproduction steps
7. Suggested fix
8. Similar defects

Format the output as a JSON object."""
        
        try:
            # 调用OpenAI API生成缺陷报告
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a QA engineer generating defect reports."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 解析响应
            report_data = json.loads(response.choices[0].message.content)
            
            # 创建缺陷报告
            defect_report = DefectReport(
                id=defect_id,
                title=report_data.get("title", "Untitled Defect"),
                description=report_data.get("description", "No description"),
                root_cause=report_data.get("root_cause", "Unknown"),
                severity=report_data.get("severity", "Medium"),
                impact=report_data.get("impact", []),
                reproduction_steps=report_data.get("reproduction_steps", []),
                suggested_fix=report_data.get("suggested_fix", "No fix suggested"),
                similar_defects=report_data.get("similar_defects", []),
                timestamp=datetime.datetime.now().isoformat()
            )
            
            # 保存缺陷报告
            self.defects.append(defect_report)
            self._save_defects()
            
            return defect_report
            
        except Exception as e:
            logger.error(f"生成缺陷报告失败: {str(e)}")
            # 返回默认缺陷报告
            return DefectReport(
                id=defect_id,
                title="Error generating report",
                description=str(e),
                root_cause="Unknown",
                severity="Medium",
                impact=[],
                reproduction_steps=[],
                suggested_fix="No fix suggested",
                similar_defects=[],
                timestamp=datetime.datetime.now().isoformat()
            )
    
    def analyze_code_dependencies(self, code_path: Optional[str] = None) -> Dict[str, Any]:
        """使用图神经网络分析代码依赖关系
        
        Args:
            code_path (Optional[str], optional): 代码路径，默认为None
            
        Returns:
            Dict[str, Any]: 依赖关系分析结果
        """
        logger.info("分析代码依赖关系")
        
        if not code_path:
            code_path = self.repo_path
        
        try:
            # 构建代码依赖图
            dependency_graph = self._build_dependency_graph(code_path)
            
            # 分析依赖图
            graph_analysis = self._analyze_dependency_graph(dependency_graph)
            
            return {
                "dependency_graph": graph_analysis,
                "node_count": len(dependency_graph.nodes),
                "edge_count": len(dependency_graph.edges)
            }
            
        except Exception as e:
            logger.error(f"分析代码依赖关系失败: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _build_dependency_graph(self, code_path: str) -> nx.DiGraph:
        """构建代码依赖图"""
        graph = nx.DiGraph()
        
        # 简单的依赖分析（实际项目中可能需要更复杂的解析）
        for root, dirs, files in os.walk(code_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    graph.add_node(file_path)
                    
                    # 尝试解析import语句
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            # 简单的import语句匹配
                            imports = re.findall(r'import\s+([\w.]+)', content)
                            from_imports = re.findall(r'from\s+([\w.]+)\s+import', content)
                            
                            for imp in imports + from_imports:
                                # 简化处理，实际项目中需要更复杂的模块解析
                                if imp.startswith("."):
                                    # 相对导入
                                    relative_path = os.path.join(os.path.dirname(file_path), imp.replace(".", os.sep) + ".py")
                                    if os.path.exists(relative_path):
                                        graph.add_edge(file_path, relative_path)
                    except Exception:
                        pass
        
        return graph
    
    def _analyze_dependency_graph(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """分析依赖图"""
        # 计算节点中心性
        centrality = nx.degree_centrality(graph)
        
        # 计算依赖深度（优化版本，避免计算所有路径）
        depths = {}
        for node in graph.nodes:
            try:
                # 使用拓扑排序计算深度，避免计算所有路径
                if nx.is_directed_acyclic_graph(graph):
                    # 对于DAG，使用拓扑排序计算深度
                    topological_order = list(nx.topological_sort(graph))
                    depth_map = {node: 0 for node in graph.nodes}
                    for n in topological_order:
                        for predecessor in graph.predecessors(n):
                            depth_map[n] = max(depth_map[n], depth_map[predecessor] + 1)
                    depths[node] = depth_map[node]
                else:
                    # 对于非DAG，使用简单的BFS计算深度
                    max_depth = 0
                    visited = set()
                    queue = [(node, 0)]
                    while queue:
                        current, depth = queue.pop(0)
                        if current in visited:
                            continue
                        visited.add(current)
                        max_depth = max(max_depth, depth)
                        for successor in graph.successors(current):
                            if successor not in visited:
                                queue.append((successor, depth + 1))
                    depths[node] = max_depth
            except Exception:
                depths[node] = 0
        
        # 识别关键节点（高中心性）
        key_nodes = [node for node, score in centrality.items() if score > 0.1]
        
        # 计算环（仅当图不是DAG时）
        cycles = []
        if not nx.is_directed_acyclic_graph(graph):
            try:
                # 限制环的数量，避免性能问题
                cycle_generator = nx.simple_cycles(graph)
                cycles = [next(cycle_generator) for _ in range(10)]  # 最多获取10个环
            except StopIteration:
                pass
        
        return {
            "centrality": centrality,
            "depths": depths,
            "key_nodes": key_nodes,
            "cycles": cycles
        }
    
    def get_defects(self) -> List[DefectReport]:
        """获取所有缺陷报告"""
        return self.defects
    
    def get_code_history(self) -> Dict[str, Any]:
        """获取代码历史数据"""
        return self.code_history