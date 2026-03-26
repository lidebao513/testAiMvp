from typing import List, Dict, Any
import openai

class TestGenerator:
    """测试生成器类，用于生成不同类型的测试代码和测试数据
    
    该类利用AI模型（如GPT-4）生成单元测试、集成测试、E2E测试和测试数据。
    
    Args:
        api_key (str): OpenAI API密钥
        model (str, optional): 使用的AI模型，默认为"gpt-4"
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """初始化测试生成器
        
        Args:
            api_key (str): OpenAI API密钥
            model (str, optional): 使用的AI模型，默认为"gpt-4"
        """
        openai.api_key = api_key
        self.model = model
    
    def generate_unit_test(self, code: str, language: str = "python") -> str:
        """生成单元测试代码
        
        利用AI模型为给定的代码生成单元测试，包括正常操作、边界情况、错误处理和边界条件的测试用例。
        
        Args:
            code (str): 要测试的代码
            language (str, optional): 代码语言，默认为"python"
            
        Returns:
            str: 生成的单元测试代码
            
        Example:
            >>> generator = TestGenerator(api_key="your-api-key")
            >>> code = "def add(a, b): return a + b"
            >>> test_code = generator.generate_unit_test(code, "python")
            >>> print(test_code)
            """
            import pytest
            
            def test_add_normal_case():
                assert add(1, 2) == 3
            
            def test_add_edge_case():
                assert add(0, 0) == 0
            
            def test_add_negative_numbers():
                assert add(-1, -2) == -3
            """
        """
        # 构建提示词，指导AI模型生成单元测试
        prompt = f"""Generate unit tests for the following {language} code:

{code}

Use the appropriate testing framework for {language} (e.g., pytest for Python, jest for JavaScript).
Include test cases for:
1. Normal operation
2. Edge cases
3. Error handling
4. Boundary conditions

Format the output as a complete test file."""
        
        # 调用OpenAI API生成单元测试
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are a QA engineer generating {language} unit tests."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回生成的测试代码
        return response.choices[0].message.content
    
    def generate_integration_test(self, api_spec: Dict[str, Any]) -> str:
        """生成API集成测试代码
        
        利用AI模型为给定的API规范生成集成测试，包括成功场景、错误场景、边界情况和认证测试（如果适用）。
        
        Args:
            api_spec (Dict[str, Any]): API规范（如OpenAPI规范）
            
        Returns:
            str: 生成的集成测试代码
            
        Example:
            >>> generator = TestGenerator(api_key="your-api-key")
            >>> spec = {"paths": {"/api/users": {"get": {"summary": "获取用户列表"}}}}
            >>> test_code = generator.generate_integration_test(spec)
            >>> print(test_code)
            """
            import requests
            
            def test_get_users():
                response = requests.get("http://localhost:8000/api/users")
                assert response.status_code == 200
                assert isinstance(response.json(), list)
            """
        """
        # 构建提示词，指导AI模型生成集成测试
        prompt = f"""Generate integration tests for the following API specification:

{api_spec}

Include test cases for:
1. Success scenarios
2. Error scenarios
3. Edge cases
4. Authentication (if applicable)

Format the output as a complete test file using an appropriate API testing framework."""
        
        # 调用OpenAI API生成集成测试
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a QA engineer generating API integration tests."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回生成的测试代码
        return response.choices[0].message.content
    
    def generate_e2e_test(self, user_flow: str, framework: str = "playwright") -> str:
        """生成E2E测试代码
        
        利用AI模型为给定的用户流程生成E2E测试，包括完整的用户旅程、边界情况、错误处理和UI交互测试。
        
        Args:
            user_flow (str): 用户流程描述
            framework (str, optional): E2E测试框架，默认为"playwright"
            
        Returns:
            str: 生成的E2E测试代码
            
        Example:
            >>> generator = TestGenerator(api_key="your-api-key")
            >>> flow = "用户打开登录页面，输入用户名和密码，点击登录按钮"
            >>> test_code = generator.generate_e2e_test(flow, "playwright")
            >>> print(test_code)
            """
            const { test, expect } = require('@playwright/test');
            
            test('用户登录测试', async ({ page }) => {
                await page.goto('http://localhost:3000/login');
                await page.fill('#username', 'testuser');
                await page.fill('#password', 'password123');
                await page.click('#login-button');
                await expect(page).toHaveURL('http://localhost:3000/home');
            });
            """
        """
        # 构建提示词，指导AI模型生成E2E测试
        prompt = f"""Generate E2E tests for the following user flow using {framework}:

{user_flow}

Include test cases for:
1. Complete user journey
2. Edge cases
3. Error handling
4. UI interactions

Format the output as a complete test file."""
        
        # 调用OpenAI API生成E2E测试
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are a QA engineer generating {framework} E2E tests."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回生成的测试代码
        return response.choices[0].message.content
    
    def generate_test_data(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成测试数据
        
        利用AI模型为给定的模式生成测试数据，包括正常情况、边界情况、边界值和无效情况。
        
        Args:
            schema (Dict[str, Any]): 数据模式
            
        Returns:
            List[Dict[str, Any]]: 生成的测试数据列表
            
        Example:
            >>> generator = TestGenerator(api_key="your-api-key")
            >>> schema = {"name": "string", "age": "integer", "email": "string"}
            >>> test_data = generator.generate_test_data(schema)
            >>> print(test_data)
            [
                {"name": "John Doe", "age": 30, "email": "john@example.com"},  # 正常情况
                {"name": "", "age": 0, "email": "invalid-email"},  # 边界情况和无效情况
                {"name": "A" * 100, "age": 120, "email": "valid@example.com"}  # 边界值
            ]
        """
        # 构建提示词，指导AI模型生成测试数据
        prompt = f"""Generate test data for the following schema:

{schema}

Include:
1. Normal cases
2. Edge cases
3. Boundary values
4. Invalid cases

Format the output as a JSON array of test data objects."""
        
        # 调用OpenAI API生成测试数据
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a QA engineer generating test data."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回生成的测试数据
        return response.choices[0].message.content