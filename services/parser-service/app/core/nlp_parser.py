from typing import List, Dict, Any
import openai
import re

class NLPParser:
    """NLP解析器类，用于解析需求文档、代码变更和API文档
    
    该类利用AI模型（如GPT-4）进行自然语言处理，从不同类型的输入中提取测试点和测试用例。
    
    Args:
        api_key (str): OpenAI API密钥
        model (str, optional): 使用的AI模型，默认为"gpt-4"
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """初始化NLP解析器
        
        Args:
            api_key (str): OpenAI API密钥
            model (str, optional): 使用的AI模型，默认为"gpt-4"
        """
        openai.api_key = api_key
        self.model = model
    
    def extract_test_points(self, requirement_text: str) -> List[Dict[str, Any]]:
        """从需求文档中提取测试点
        
        利用AI模型分析需求文档，提取出测试点，包括测试用例描述、测试步骤、预期结果、优先级和测试类型。
        
        Args:
            requirement_text (str): 需求文档文本
            
        Returns:
            List[Dict[str, Any]]: 测试点列表，每个测试点包含描述、步骤、预期结果、优先级和测试类型
            
        Example:
            >>> parser = NLPParser(api_key="your-api-key")
            >>> requirement = "用户可以登录系统，输入正确的用户名和密码后跳转到首页"
            >>> test_points = parser.extract_test_points(requirement)
            >>> print(test_points)
            [{
                "test_case_description": "用户登录测试",
                "test_steps": ["1. 打开登录页面", "2. 输入正确的用户名和密码", "3. 点击登录按钮"],
                "expected_result": "用户成功登录并跳转到首页",
                "priority": "High",
                "test_type": "E2E"
            }]
        """
        # 构建提示词，指导AI模型提取测试点
        prompt = f"""Extract test points from the following requirement document:

{requirement_text}

For each test point, provide:
1. Test case description
2. Test steps
3. Expected result
4. Priority (High/Medium/Low)
5. Test type (Unit/Integration/E2E)

Format the output as a JSON array of objects."""
        
        # 调用OpenAI API生成测试点
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a QA engineer extracting test points from requirements."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回生成的测试点
        return response.choices[0].message.content

    def analyze_code_diff(self, diff_text: str) -> List[Dict[str, Any]]:
        """分析代码变更并识别需要更新或添加的测试用例
        
        利用AI模型分析代码变更，识别出受影响的功能和需要的测试类型。
        
        Args:
            diff_text (str): 代码变更的diff文本
            
        Returns:
            List[Dict[str, Any]]: 测试用例列表，每个测试用例包含受影响的功能、需要的测试类型、测试原因和优先级
            
        Example:
            >>> parser = NLPParser(api_key="your-api-key")
            >>> diff = "- def add(a, b):\n+ def add(a, b, c=0):\n     return a + b + c"
            >>> test_cases = parser.analyze_code_diff(diff)
            >>> print(test_cases)
            [{
                "affected_functionality": "add函数",
                "type_of_test_needed": "Unit",
                "reason_for_test": "函数签名变更，添加了默认参数c",
                "priority": "Medium"
            }]
        """
        # 构建提示词，指导AI模型分析代码变更
        prompt = f"""Analyze the following code diff and identify potential test cases that need to be updated or added:

{diff_text}

For each potential test case, provide:
1. Affected functionality
2. Type of test needed (Unit/Integration/E2E)
3. Reason for test
4. Priority (High/Medium/Low)

Format the output as a JSON array of objects."""
        
        # 调用OpenAI API分析代码变更
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a QA engineer analyzing code changes."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回分析结果
        return response.choices[0].message.content

    def parse_openapi_spec(self, openapi_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析OpenAPI规范并生成测试用例
        
        从OpenAPI规范中提取端点信息，生成对应的测试用例。
        
        Args:
            openapi_spec (Dict[str, Any]): OpenAPI规范的字典表示
            
        Returns:
            List[Dict[str, Any]]: 测试用例列表，每个测试用例包含端点、描述、请求体和响应信息
            
        Example:
            >>> parser = NLPParser(api_key="your-api-key")
            >>> spec = {"paths": {"/api/users": {"get": {"summary": "获取用户列表"}}}}
            >>> test_cases = parser.parse_openapi_spec(spec)
            >>> print(test_cases)
            [{
                "endpoint": "GET /api/users",
                "description": "获取用户列表",
                "request_body": None,
                "responses": {}
            }]
        """
        test_cases = []
        
        # 从OpenAPI规范中提取paths部分
        paths = openapi_spec.get("paths", {})
        
        # 遍历每个路径和方法
        for path, methods in paths.items():
            for method, details in methods.items():
                # 构建测试用例
                test_case = {
                    "endpoint": f"{method.upper()} {path}",  # 构建端点字符串，如"GET /api/users"
                    "description": details.get("summary", ""),  # 获取端点描述
                    "request_body": details.get("requestBody", None),  # 获取请求体信息
                    "responses": details.get("responses", {})  # 获取响应信息
                }
                test_cases.append(test_case)
        
        return test_cases