from typing import List, Dict, Any, Optional, Tuple
import os
import json
import time
import logging
import datetime
import re
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SelfHealer")

@dataclass
class HealingAction:
    """自愈操作类"""
    id: str
    type: str  # ui_locator, api_assertion, test_data
    test_id: str
    original_value: Any
    new_value: Any
    timestamp: str
    confidence: float
    status: str  # pending, applied, rejected

@dataclass
class UIElement:
    """UI元素类"""
    id: str
    name: str
    locators: List[Dict[str, str]]  # 多种定位方式
    last_updated: str
    page: str

class SelfHealer:
    """测试自愈服务"""
    
    def __init__(self, storage_path: str = "./self_healing_data"):
        """初始化自愈服务
        
        Args:
            storage_path (str, optional): 数据存储路径，默认为"./self_healing_data"
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # 初始化存储文件
        self.elements_file = self.storage_path / "ui_elements.json"
        self.healing_actions_file = self.storage_path / "healing_actions.json"
        self.knowledge_graph_file = self.storage_path / "knowledge_graph.json"
        
        # 加载数据
        self.ui_elements = self._load_ui_elements()
        self.healing_actions = self._load_healing_actions()
        self.knowledge_graph = self._load_knowledge_graph()
    
    def _load_ui_elements(self) -> Dict[str, UIElement]:
        """加载UI元素数据"""
        if self.elements_file.exists():
            with open(self.elements_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                elements = {}
                for elem_id, elem_data in data.items():
                    elements[elem_id] = UIElement(
                        id=elem_data["id"],
                        name=elem_data["name"],
                        locators=elem_data["locators"],
                        last_updated=elem_data["last_updated"],
                        page=elem_data["page"]
                    )
                return elements
        return {}
    
    def _load_healing_actions(self) -> List[HealingAction]:
        """加载自愈操作数据"""
        if self.healing_actions_file.exists():
            with open(self.healing_actions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                actions = []
                for action_data in data:
                    actions.append(HealingAction(
                        id=action_data["id"],
                        type=action_data["type"],
                        test_id=action_data["test_id"],
                        original_value=action_data["original_value"],
                        new_value=action_data["new_value"],
                        timestamp=action_data["timestamp"],
                        confidence=action_data["confidence"],
                        status=action_data["status"]
                    ))
                return actions
        return []
    
    def _load_knowledge_graph(self) -> Dict[str, Any]:
        """加载知识图谱数据"""
        if self.knowledge_graph_file.exists():
            with open(self.knowledge_graph_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"nodes": [], "edges": []}
    
    def _save_ui_elements(self):
        """保存UI元素数据"""
        data = {}
        for elem_id, elem in self.ui_elements.items():
            data[elem_id] = {
                "id": elem.id,
                "name": elem.name,
                "locators": elem.locators,
                "last_updated": elem.last_updated,
                "page": elem.page
            }
        with open(self.elements_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_healing_actions(self):
        """保存自愈操作数据"""
        data = []
        for action in self.healing_actions:
            data.append({
                "id": action.id,
                "type": action.type,
                "test_id": action.test_id,
                "original_value": action.original_value,
                "new_value": action.new_value,
                "timestamp": action.timestamp,
                "confidence": action.confidence,
                "status": action.status
            })
        with open(self.healing_actions_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_knowledge_graph(self):
        """保存知识图谱数据"""
        with open(self.knowledge_graph_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_graph, f, ensure_ascii=False, indent=2)
    
    def heal_ui_locator(self, test_id: str, element_name: str, page: str, current_locator: Dict[str, str], page_source: str) -> Optional[Dict[str, str]]:
        """自愈UI元素定位
        
        Args:
            test_id (str): 测试ID
            element_name (str): 元素名称
            page (str): 页面名称
            current_locator (Dict[str, str]): 当前定位器
            page_source (str): 页面源代码
            
        Returns:
            Optional[Dict[str, str]]: 新的定位器，失败返回None
        """
        logger.info(f"尝试自愈UI元素定位: {element_name} on page {page}")
        
        # 生成元素ID
        element_id = f"{page}_{element_name}"
        
        # 从页面源代码中提取可能的定位器
        possible_locators = self._extract_possible_locators(page_source, element_name)
        
        if not possible_locators:
            logger.warning(f"无法为元素 {element_name} 提取新的定位器")
            return None
        
        # 选择最佳定位器
        best_locator = self._select_best_locator(possible_locators)
        
        # 更新UI元素信息
        if element_id not in self.ui_elements:
            self.ui_elements[element_id] = UIElement(
                id=element_id,
                name=element_name,
                locators=[best_locator],
                last_updated=datetime.datetime.now().isoformat(),
                page=page
            )
        else:
            # 添加新的定位器（如果不存在）
            locator_strs = [json.dumps(loc) for loc in self.ui_elements[element_id].locators]
            if json.dumps(best_locator) not in locator_strs:
                self.ui_elements[element_id].locators.append(best_locator)
                self.ui_elements[element_id].last_updated = datetime.datetime.now().isoformat()
        
        # 保存UI元素数据
        self._save_ui_elements()
        
        # 记录自愈操作
        action_id = f"heal_{int(time.time())}"
        action = HealingAction(
            id=action_id,
            type="ui_locator",
            test_id=test_id,
            original_value=current_locator,
            new_value=best_locator,
            timestamp=datetime.datetime.now().isoformat(),
            confidence=0.9,  # 假设高置信度
            status="pending"
        )
        self.healing_actions.append(action)
        self._save_healing_actions()
        
        # 更新知识图谱
        self._update_knowledge_graph(element_id, "ui_element", "updated")
        
        logger.info(f"成功自愈UI元素定位: {element_name} -> {best_locator}")
        return best_locator
    
    def _extract_possible_locators(self, page_source: str, element_name: str) -> List[Dict[str, str]]:
        """从页面源代码中提取可能的定位器"""
        locators = []
        
        # 尝试通过id定位
        id_pattern = re.compile(r'id=["\']([^"\']+)["\'].*?' + re.escape(element_name), re.IGNORECASE)
        for match in id_pattern.finditer(page_source):
            locators.append({"id": match.group(1)})
        
        # 尝试通过class定位
        class_pattern = re.compile(r'class=["\']([^"\']+)["\'].*?' + re.escape(element_name), re.IGNORECASE)
        for match in class_pattern.finditer(page_source):
            locators.append({"class": match.group(1).split()[0]})  # 使用第一个class
        
        # 尝试通过name定位
        name_pattern = re.compile(r'name=["\']([^"\']+)["\'].*?' + re.escape(element_name), re.IGNORECASE)
        for match in name_pattern.finditer(page_source):
            locators.append({"name": match.group(1)})
        
        # 尝试通过xpath定位
        # 这里简化处理，实际项目中可能需要更复杂的xpath生成逻辑
        if element_name in page_source:
            locators.append({"xpath": f"//*[contains(text(), '{element_name}')]"})
        
        return locators
    
    def _select_best_locator(self, locators: List[Dict[str, str]]) -> Dict[str, str]:
        """选择最佳定位器"""
        # 优先级：id > name > class > xpath
        priority = ["id", "name", "class", "xpath"]
        
        for locator_type in priority:
            for locator in locators:
                if locator_type in locator:
                    return locator
        
        return locators[0] if locators else {}
    
    def heal_api_assertion(self, test_id: str, endpoint: str, original_assertion: Dict[str, Any], actual_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """自愈API响应断言
        
        Args:
            test_id (str): 测试ID
            endpoint (str): API端点
            original_assertion (Dict[str, Any]): 原始断言
            actual_response (Dict[str, Any]): 实际响应
            
        Returns:
            Optional[Dict[str, Any]]: 新的断言，失败返回None
        """
        logger.info(f"尝试自愈API断言: {endpoint}")
        
        # 分析响应结构变化
        new_assertion = self._analyze_response_structure(original_assertion, actual_response)
        
        if not new_assertion:
            logger.warning(f"无法为API {endpoint} 更新断言")
            return None
        
        # 记录自愈操作
        action_id = f"heal_{int(time.time())}"
        action = HealingAction(
            id=action_id,
            type="api_assertion",
            test_id=test_id,
            original_value=original_assertion,
            new_value=new_assertion,
            timestamp=datetime.datetime.now().isoformat(),
            confidence=0.85,  # 中等置信度
            status="pending"
        )
        self.healing_actions.append(action)
        self._save_healing_actions()
        
        # 更新知识图谱
        self._update_knowledge_graph(endpoint, "api_endpoint", "updated")
        
        logger.info(f"成功自愈API断言: {endpoint}")
        return new_assertion
    
    def _analyze_response_structure(self, original: Dict[str, Any], actual: Dict[str, Any]) -> Dict[str, Any]:
        """分析响应结构并更新断言"""
        new_assertion = {}
        
        # 遍历原始断言的键
        for key, expected_value in original.items():
            if key in actual:
                # 键存在，检查值类型
                if isinstance(expected_value, dict) and isinstance(actual[key], dict):
                    # 递归处理嵌套字典
                    nested_assertion = self._analyze_response_structure(expected_value, actual[key])
                    if nested_assertion:
                        new_assertion[key] = nested_assertion
                else:
                    # 键存在，使用实际值类型作为新的断言
                    new_assertion[key] = type(actual[key]).__name__  # 存储类型名称
            else:
                # 键不存在，记录为缺失
                new_assertion[key] = "MISSING"
        
        # 添加新出现的键
        for key in actual:
            if key not in original:
                new_assertion[key] = type(actual[key]).__name__
        
        return new_assertion
    
    def heal_test_data(self, test_id: str, data_type: str, original_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """自愈测试数据
        
        Args:
            test_id (str): 测试ID
            data_type (str): 数据类型
            original_data (Dict[str, Any]): 原始数据
            
        Returns:
            Optional[Dict[str, Any]]: 新的数据，失败返回None
        """
        logger.info(f"尝试自愈测试数据: {data_type}")
        
        # 生成新的测试数据
        new_data = self._generate_test_data(data_type, original_data)
        
        if not new_data:
            logger.warning(f"无法为数据类型 {data_type} 生成新数据")
            return None
        
        # 记录自愈操作
        action_id = f"heal_{int(time.time())}"
        action = HealingAction(
            id=action_id,
            type="test_data",
            test_id=test_id,
            original_value=original_data,
            new_value=new_data,
            timestamp=datetime.datetime.now().isoformat(),
            confidence=0.8,  # 中等置信度
            status="pending"
        )
        self.healing_actions.append(action)
        self._save_healing_actions()
        
        # 更新知识图谱
        self._update_knowledge_graph(data_type, "test_data", "updated")
        
        logger.info(f"成功自愈测试数据: {data_type}")
        return new_data
    
    def _generate_test_data(self, data_type: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试数据"""
        new_data = {}
        
        # 根据数据类型生成新数据
        for key, value in original_data.items():
            if isinstance(value, str):
                # 字符串类型，生成类似的字符串
                if key.lower() in ["email"]:
                    new_data[key] = f"test_{int(time.time())}@example.com"
                elif key.lower() in ["name", "username"]:
                    new_data[key] = f"TestUser_{int(time.time())}"
                elif key.lower() in ["password"]:
                    new_data[key] = f"Password123!{int(time.time())}"
                else:
                    new_data[key] = f"{value}_{int(time.time())}"
            elif isinstance(value, int):
                # 数字类型，生成类似的数字
                new_data[key] = value + int(time.time()) % 1000
            elif isinstance(value, bool):
                # 布尔类型，取反
                new_data[key] = not value
            elif isinstance(value, list):
                # 列表类型，生成类似的列表
                new_data[key] = value.copy()
                if new_data[key]:
                    new_data[key][0] = self._generate_test_data(f"{data_type}_{key}", new_data[key][0])
            elif isinstance(value, dict):
                # 字典类型，递归生成
                new_data[key] = self._generate_test_data(f"{data_type}_{key}", value)
            else:
                # 其他类型，保持不变
                new_data[key] = value
        
        return new_data
    
    def _update_knowledge_graph(self, entity_id: str, entity_type: str, action: str):
        """更新知识图谱"""
        # 检查节点是否存在
        node_exists = False
        for node in self.knowledge_graph["nodes"]:
            if node["id"] == entity_id:
                node_exists = True
                node["last_updated"] = datetime.datetime.now().isoformat()
                break
        
        if not node_exists:
            # 添加新节点
            self.knowledge_graph["nodes"].append({
                "id": entity_id,
                "type": entity_type,
                "created": datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat()
            })
        
        # 添加边
        edge_id = f"edge_{int(time.time())}"
        self.knowledge_graph["edges"].append({
            "id": edge_id,
            "source": entity_id,
            "target": "system",
            "action": action,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # 保存知识图谱
        self._save_knowledge_graph()
    
    def get_pending_actions(self) -> List[HealingAction]:
        """获取待审核的自愈操作"""
        return [action for action in self.healing_actions if action.status == "pending"]
    
    def approve_action(self, action_id: str):
        """批准自愈操作"""
        for action in self.healing_actions:
            if action.id == action_id:
                action.status = "applied"
                logger.info(f"批准自愈操作: {action_id}")
                self._save_healing_actions()
                return True
        return False
    
    def reject_action(self, action_id: str):
        """拒绝自愈操作"""
        for action in self.healing_actions:
            if action.id == action_id:
                action.status = "rejected"
                logger.info(f"拒绝自愈操作: {action_id}")
                self._save_healing_actions()
                return True
        return False
    
    def get_ui_elements(self) -> Dict[str, UIElement]:
        """获取所有UI元素"""
        return self.ui_elements
    
    def get_knowledge_graph(self) -> Dict[str, Any]:
        """获取知识图谱"""
        return self.knowledge_graph

if __name__ == "__main__":
    # 示例用法
    healer = SelfHealer()
    
    # 示例1: 自愈UI元素定位
    test_id = "test-1"
    element_name = "登录按钮"
    page = "login"
    current_locator = {"id": "login-btn"}
    page_source = """
    <div class="login-form">
        <h2>用户登录</h2>
        <input type="text" id="username" placeholder="用户名">
        <input type="password" id="password" placeholder="密码">
        <button class="btn-login" id="new-login-btn">登录</button>
    </div>
    """
    
    new_locator = healer.heal_ui_locator(test_id, element_name, page, current_locator, page_source)
    print(f"新的定位器: {new_locator}")
    
    # 示例2: 自愈API断言
    test_id = "test-2"
    endpoint = "/api/users"
    original_assertion = {
        "status": "success",
        "data": {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com"
        }
    }
    actual_response = {
        "status": "success",
        "data": {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "created_at": "2023-01-01T00:00:00Z"
        },
        "meta": {
            "page": 1,
            "total": 100
        }
    }
    
    new_assertion = healer.heal_api_assertion(test_id, endpoint, original_assertion, actual_response)
    print(f"新的断言: {new_assertion}")
    
    # 示例3: 自愈测试数据
    test_id = "test-3"
    data_type = "user_registration"
    original_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!"
    }
    
    new_data = healer.heal_test_data(test_id, data_type, original_data)
    print(f"新的测试数据: {new_data}")
    
    # 获取待审核的操作
    pending_actions = healer.get_pending_actions()
    print(f"待审核的操作数量: {len(pending_actions)}")
    
    # 批准第一个操作
    if pending_actions:
        healer.approve_action(pending_actions[0].id)
        print(f"已批准操作: {pending_actions[0].id}")
    
    # 获取知识图谱
    knowledge_graph = healer.get_knowledge_graph()
    print(f"知识图谱节点数量: {len(knowledge_graph['nodes'])}")
    print(f"知识图谱边数量: {len(knowledge_graph['edges'])}")
