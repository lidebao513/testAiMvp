from typing import List, Dict, Any, Optional
import os
import json
import xml.etree.ElementTree as ET
import pandas as pd
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TestCaseGenerator:
    """多策略测试用例生成器
    
    能够基于不同输入生成多种类型的测试用例，支持多种输出格式，
    集成测试设计方法，自动评估用例质量，使用Few-shot learning提升生成质量。
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """初始化测试用例生成器
        
        Args:
            api_key (str): OpenAI API密钥
            model (str, optional): 使用的AI模型，默认为"gpt-4"
        """
        self.llm = OpenAI(api_key=api_key, model=model, temperature=0.3)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self._init_prompts()
    
    def _init_prompts(self):
        """初始化提示词模板"""
        # 基于需求生成功能测试用例的提示词
        self.functional_test_prompt = PromptTemplate(
            input_variables=["requirements"],
            template="""
你是一个专业的测试工程师，请根据以下需求生成功能测试用例：

{requirements}

请使用以下测试设计方法：
1. 等价类划分
2. 边界值分析
3. 场景法

每个测试用例应包含：
- 测试用例ID
- 测试用例名称
- 测试目的
- 测试环境
- 测试步骤
- 预期结果
- 优先级
- 测试类型

请以JSON格式输出，包含以下字段：
- test_cases: 测试用例列表
- test_design_methods: 使用的测试设计方法
- coverage_analysis: 覆盖度分析
"""
        )
        
        # 基于代码生成单元测试的提示词
        self.unit_test_prompt = PromptTemplate(
            input_variables=["code", "language"],
            template="""
你是一个专业的测试工程师，请根据以下代码生成单元测试：

语言: {language}

代码:
{code}

请为每个函数生成详细的单元测试，包括：
1. 正常情况测试
2. 边界值测试
3. 异常情况测试
4. 特殊输入测试

请使用该语言的标准测试框架，并以完整的测试文件格式输出。
"""
        )
        
        # 基于API规范生成接口测试的提示词
        self.api_test_prompt = PromptTemplate(
            input_variables=["api_spec"],
            template="""
你是一个专业的测试工程师，请根据以下API规范生成接口测试用例：

{api_spec}

请为每个接口生成详细的测试用例，包括：
1. 接口URL
2. 请求方法
3. 请求参数
4. 预期响应
5. 测试场景（正常、异常、边界值等）

请以JSON格式输出，包含以下字段：
- test_cases: 测试用例列表
- endpoint_coverage: 端点覆盖情况
"""
        )
        
        # 基于用户行为生成探索性测试用例的提示词
        self.exploratory_test_prompt = PromptTemplate(
            input_variables=["user_behaviors"],
            template="""
你是一个专业的测试工程师，请根据以下用户行为描述生成探索性测试用例：

{user_behaviors}

请生成详细的探索性测试用例，包括：
1. 测试场景
2. 测试步骤
3. 观察点
4. 可能的问题
5. 优先级

请以JSON格式输出，包含以下字段：
- test_cases: 测试用例列表
- behavior_coverage: 行为覆盖情况
"""
        )
        
        # 初始化LLM链
        self.functional_test_chain = LLMChain(llm=self.llm, prompt=self.functional_test_prompt)
        self.unit_test_chain = LLMChain(llm=self.llm, prompt=self.unit_test_prompt)
        self.api_test_chain = LLMChain(llm=self.llm, prompt=self.api_test_prompt)
        self.exploratory_test_chain = LLMChain(llm=self.llm, prompt=self.exploratory_test_prompt)
    
    def generate_functional_tests(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """基于需求生成功能测试用例
        
        Args:
            requirements (Dict[str, Any]): 解析后的需求
            
        Returns:
            Dict[str, Any]: 生成的测试用例
        """
        requirements_str = json.dumps(requirements, ensure_ascii=False)
        result = self.functional_test_chain.run(requirements_str)
        
        try:
            test_cases_data = json.loads(result)
            return test_cases_data
        except json.JSONDecodeError:
            raise ValueError(f"生成功能测试用例失败: {result}")
    
    def generate_unit_tests(self, code: str, language: str = "python") -> str:
        """基于代码生成单元测试
        
        Args:
            code (str): 代码内容
            language (str, optional): 代码语言，默认为"python"
            
        Returns:
            str: 生成的单元测试代码
        """
        result = self.unit_test_chain.run(code=code, language=language)
        return result
    
    def generate_api_tests(self, api_spec: Dict[str, Any]) -> Dict[str, Any]:
        """基于API规范生成接口测试
        
        Args:
            api_spec (Dict[str, Any]): API规范
            
        Returns:
            Dict[str, Any]: 生成的接口测试用例
        """
        api_spec_str = json.dumps(api_spec, ensure_ascii=False)
        result = self.api_test_chain.run(api_spec_str)
        
        try:
            test_cases_data = json.loads(result)
            return test_cases_data
        except json.JSONDecodeError:
            raise ValueError(f"生成接口测试用例失败: {result}")
    
    def generate_exploratory_tests(self, user_behaviors: str) -> Dict[str, Any]:
        """基于用户行为生成探索性测试用例
        
        Args:
            user_behaviors (str): 用户行为描述
            
        Returns:
            Dict[str, Any]: 生成的探索性测试用例
        """
        result = self.exploratory_test_chain.run(user_behaviors)
        
        try:
            test_cases_data = json.loads(result)
            return test_cases_data
        except json.JSONDecodeError:
            raise ValueError(f"生成探索性测试用例失败: {result}")
    
    def evaluate_test_quality(self, test_cases: List[Dict[str, Any]], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """评估测试用例质量
        
        Args:
            test_cases (List[Dict[str, Any]]): 测试用例列表
            requirements (Dict[str, Any]): 需求信息
            
        Returns:
            Dict[str, Any]: 质量评估结果
        """
        # 简单的质量评估逻辑
        functional_points = requirements.get("functional_points", [])
        total_functional_points = len(functional_points)
        
        # 计算覆盖度
        covered_points = set()
        for test_case in test_cases:
            test_name = test_case.get("name", "")
            for point in functional_points:
                point_name = point.get("name", "") if isinstance(point, dict) else str(point)
                if point_name.lower() in test_name.lower():
                    covered_points.add(point_name)
        
        coverage_rate = len(covered_points) / total_functional_points if total_functional_points > 0 else 0
        
        # 计算冗余度（简单的基于测试名称相似度）
        test_names = [test.get("name", "").lower() for test in test_cases]
        redundancy_count = 0
        for i in range(len(test_names)):
            for j in range(i + 1, len(test_names)):
                if test_names[i] in test_names[j] or test_names[j] in test_names[i]:
                    redundancy_count += 1
        
        redundancy_rate = redundancy_count / len(test_cases) if len(test_cases) > 0 else 0
        
        return {
            "coverage_rate": coverage_rate,
            "redundancy_rate": redundancy_rate,
            "total_test_cases": len(test_cases),
            "covered_functional_points": len(covered_points),
            "total_functional_points": total_functional_points
        }
    
    def export_to_json(self, test_cases: List[Dict[str, Any]], output_path: str):
        """导出测试用例到JSON文件
        
        Args:
            test_cases (List[Dict[str, Any]]): 测试用例列表
            output_path (str): 输出文件路径
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(test_cases, f, ensure_ascii=False, indent=2)
        print(f"测试用例已导出到: {output_path}")
    
    def export_to_excel(self, test_cases: List[Dict[str, Any]], output_path: str):
        """导出测试用例到Excel文件
        
        Args:
            test_cases (List[Dict[str, Any]]): 测试用例列表
            output_path (str): 输出文件路径
        """
        # 转换测试用例为DataFrame
        df = pd.DataFrame(test_cases)
        
        # 保存到Excel文件
        df.to_excel(output_path, index=False)
        print(f"测试用例已导出到: {output_path}")
    
    def export_to_junit_xml(self, test_cases: List[Dict[str, Any]], output_path: str):
        """导出测试用例到JUnit XML文件
        
        Args:
            test_cases (List[Dict[str, Any]]): 测试用例列表
            output_path (str): 输出文件路径
        """
        # 创建根元素
        testsuites = ET.Element("testsuites")
        testsuite = ET.SubElement(testsuites, "testsuite", name="Generated Tests", tests=str(len(test_cases)))
        
        # 添加测试用例
        for i, test_case in enumerate(test_cases):
            testcase = ET.SubElement(testsuite, "testcase", 
                                   name=test_case.get("name", f"Test {i+1}"),
                                   classname="generated.tests")
            
            # 添加测试步骤作为注释
            steps = test_case.get("steps", [])
            if steps:
                steps_str = "\n".join(steps)
                ET.SubElement(testcase, "system-out").text = f"Steps:\n{steps_str}"
            
            # 添加预期结果
            expected = test_case.get("expected_result", "")
            if expected:
                ET.SubElement(testcase, "system-err").text = f"Expected: {expected}"
        
        # 写入文件
        tree = ET.ElementTree(testsuites)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"测试用例已导出到: {output_path}")
    
    def export_test_cases(self, test_cases: List[Dict[str, Any]], output_path: str, format: str = "json"):
        """导出测试用例到指定格式
        
        Args:
            test_cases (List[Dict[str, Any]]): 测试用例列表
            output_path (str): 输出文件路径
            format (str, optional): 输出格式，可选值: json, excel, junit
        """
        if format == "json":
            self.export_to_json(test_cases, output_path)
        elif format == "excel":
            self.export_to_excel(test_cases, output_path)
        elif format == "junit":
            self.export_to_junit_xml(test_cases, output_path)
        else:
            raise ValueError(f"不支持的输出格式: {format}")

if __name__ == "__main__":
    # 示例用法
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print("请设置OPENAI_API_KEY环境变量")
        exit(1)
    
    generator = TestCaseGenerator(api_key=api_key)
    
    # 示例1: 基于需求生成功能测试用例
    sample_requirements = {
        "functional_points": [
            {"name": "用户注册", "description": "支持邮箱和手机号注册"},
            {"name": "用户登录", "description": "支持邮箱/手机号+密码登录"}
        ],
        "user_stories": [
            "作为新用户，我希望能够通过邮箱或手机号注册账号，以便使用系统的各项功能。"
        ],
        "acceptance_criteria": [
            "输入有效的邮箱/手机号和密码后，能够成功注册",
            "密码强度不符合要求时，系统应给出提示"
        ]
    }
    
    functional_tests = generator.generate_functional_tests(sample_requirements)
    print("生成的功能测试用例:")
    print(json.dumps(functional_tests, ensure_ascii=False, indent=2))
    
    # 评估测试用例质量
    quality = generator.evaluate_test_quality(functional_tests.get("test_cases", []), sample_requirements)
    print("\n测试用例质量评估:")
    print(json.dumps(quality, ensure_ascii=False, indent=2))
    
    # 导出测试用例
    generator.export_test_cases(functional_tests.get("test_cases", []), "functional_tests.json", "json")
    generator.export_test_cases(functional_tests.get("test_cases", []), "functional_tests.xlsx", "excel")
    generator.export_test_cases(functional_tests.get("test_cases", []), "functional_tests.xml", "junit")
    
    # 示例2: 基于代码生成单元测试
    sample_code = """
def add(a, b):
    """Add two numbers"""
    return a + b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b
"""
    
    unit_tests = generator.generate_unit_tests(sample_code, "python")
    print("\n生成的单元测试:")
    print(unit_tests)
    
    # 保存单元测试
    with open("unit_tests.py", "w", encoding="utf-8") as f:
        f.write(unit_tests)
    print("\n单元测试已保存到: unit_tests.py")