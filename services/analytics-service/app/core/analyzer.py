from typing import List, Dict, Any
import openai
import coverage
import matplotlib.pyplot as plt
import io
import base64

class TestAnalyzer:
    """测试分析器类，用于分析测试结果和预测缺陷
    
    该类提供了测试覆盖率分析、缺陷预测、测试用例优先级排序和失败根因分析等功能。
    
    Args:
        api_key (str): OpenAI API密钥
        model (str, optional): 使用的AI模型，默认为"gpt-4"
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """初始化测试分析器
        
        Args:
            api_key (str): OpenAI API密钥
            model (str, optional): 使用的AI模型，默认为"gpt-4"
        """
        openai.api_key = api_key
        self.model = model
    
    def analyze_coverage(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析测试覆盖率
        
        分析测试覆盖率数据，计算覆盖率统计信息并生成覆盖率报告。
        
        Args:
            coverage_data (Dict[str, Any]): 覆盖率数据
            
        Returns:
            Dict[str, Any]: 覆盖率报告，包含总行数、覆盖行数、覆盖率百分比和未覆盖文件列表
            
        Example:
            >>> analyzer = TestAnalyzer(api_key="your-api-key")
            >>> coverage_data = {
            ...     "lines": {"file1.py": 10, "file2.py": 5},
            ...     "files": {"file1.py": {1: 1, 2: 1, 3: 0}, "file2.py": {1: 1, 2: 1, 3: 1}}
            ... }
            >>> report = analyzer.analyze_coverage(coverage_data)
            >>> print(report)
            {
                "total_lines": 15,
                "covered_lines": 2,
                "coverage_percentage": 13.333333333333334,
                "uncovered_files": []
            }
        """
        # 计算覆盖率统计
        total_lines = sum(coverage_data.get("lines", {}).values())
        covered_lines = sum(1 for count in coverage_data.get("lines", {}).values() if count > 0)
        coverage_percentage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
        
        # 生成覆盖率报告
        report = {
            "total_lines": total_lines,
            "covered_lines": covered_lines,
            "coverage_percentage": coverage_percentage,
            "uncovered_files": [
                file for file, lines in coverage_data.get("files", {}).items()
                if sum(lines.values()) == 0
            ]
        }
        
        return report
    
    def predict_defects(self, code_change: str) -> List[Dict[str, Any]]:
        """基于代码变更预测潜在缺陷
        
        利用AI模型分析代码变更，预测可能存在的缺陷。
        
        Args:
            code_change (str): 代码变更的diff文本
            
        Returns:
            List[Dict[str, Any]]: 潜在缺陷列表，每个缺陷包含描述、可能性、影响和建议修复方案
            
        Example:
            >>> analyzer = TestAnalyzer(api_key="your-api-key")
            >>> diff = "- def add(a, b):\n+ def add(a, b, c=0):\n     return a + b + c"
            >>> defects = analyzer.predict_defects(diff)
            >>> print(defects)
            [{
                "description": "缺少对新参数c的类型检查",
                "likelihood": "Medium",
                "impact": "Low",
                "suggested_fix": "添加类型检查，确保c是数字类型"
            }]
        """
        # 构建提示词，指导AI模型预测缺陷
        prompt = f"""Analyze the following code change and predict potential defects:

{code_change}

For each potential defect, provide:
1. Description of the defect
2. Likelihood (High/Medium/Low)
3. Impact (High/Medium/Low)
4. Suggested fix

Format the output as a JSON array of objects."""
        
        # 调用OpenAI API预测缺陷
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a QA engineer analyzing code for potential defects."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回预测结果
        return response.choices[0].message.content
    
    def prioritize_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """基于风险和影响对测试用例进行优先级排序
        
        根据测试类型和优先级计算得分，对测试用例进行排序。
        
        Args:
            test_cases (List[Dict[str, Any]]): 测试用例列表
            
        Returns:
            List[Dict[str, Any]]: 按优先级排序的测试用例列表
            
        Example:
            >>> analyzer = TestAnalyzer(api_key="your-api-key")
            >>> test_cases = [
            ...     {"test_type": "Unit", "priority": "Low"},
            ...     {"test_type": "E2E", "priority": "High"},
            ...     {"test_type": "Integration", "priority": "Medium"}
            ... ]
            >>> prioritized = analyzer.prioritize_test_cases(test_cases)
            >>> print([t.get("priority_score") for t in prioritized])
            [5, 3, 1]
        """
        # 简单的优先级排序逻辑
        for test in test_cases:
            # 基于测试类型和优先级计算得分
            priority_score = 0
            if test.get("priority") == "High":
                priority_score += 3
            elif test.get("priority") == "Medium":
                priority_score += 2
            else:
                priority_score += 1
            
            if test.get("test_type") == "E2E":
                priority_score += 2
            elif test.get("test_type") == "Integration":
                priority_score += 1
            
            test["priority_score"] = priority_score
        
        # 按优先级得分排序
        return sorted(test_cases, key=lambda x: x.get("priority_score", 0), reverse=True)
    
    def analyze_failure_root_cause(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析测试失败的根因
        
        利用AI模型分析测试失败数据，识别根因并提供修复建议。
        
        Args:
            failure_data (Dict[str, Any]): 测试失败数据
            
        Returns:
            Dict[str, Any]: 根因分析结果，包含根因分析、可能的修复方案和预防措施
            
        Example:
            >>> analyzer = TestAnalyzer(api_key="your-api-key")
            >>> failure_data = {
            ...     "test_name": "test_login",
            ...     "error": "AssertionError: Expected 200, got 401",
            ...     "stack_trace": "..."
            ... }
            >>> analysis = analyzer.analyze_failure_root_cause(failure_data)
            >>> print(analysis)
            {
                "root_cause": "认证失败，可能是密码错误或令牌过期",
                "possible_fixes": ["检查测试用例中的凭据", "确保令牌有效"],
                "prevention_measures": ["使用环境变量存储凭据", "添加令牌刷新逻辑"]
            }
        """
        # 构建提示词，指导AI模型分析失败根因
        prompt = f"""Analyze the following test failure data and identify the root cause:

{failure_data}

Provide:
1. Root cause analysis
2. Possible fixes
3. Prevention measures

Format the output as a JSON object."""
        
        # 调用OpenAI API分析失败根因
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a QA engineer analyzing test failures."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回分析结果
        return response.choices[0].message.content
    
    def generate_coverage_report(self, coverage_data: Dict[str, Any]) -> str:
        """生成带有可视化的覆盖率报告
        
        生成覆盖率图表并返回base64编码的图像。
        
        Args:
            coverage_data (Dict[str, Any]): 覆盖率数据
            
        Returns:
            str: base64编码的覆盖率图表图像
            
        Example:
            >>> analyzer = TestAnalyzer(api_key="your-api-key")
            >>> coverage_data = {
            ...     "files": {"file1.py": {1: 1, 2: 1, 3: 0}, "file2.py": {1: 1, 2: 1, 3: 1}}
            ... }
            >>> report = analyzer.generate_coverage_report(coverage_data)
            >>> print(report[:20])  # 输出前20个字符
            "data:image/png;base64,iVBORw0K"
        """
        # 生成覆盖率图表
        plt.figure(figsize=(10, 6))
        files = list(coverage_data.get("files", {}).keys())
        coverage_percentages = []
        
        # 计算每个文件的覆盖率
        for file in files:
            lines = coverage_data.get("files", {}).get(file, {})
            total = len(lines)
            covered = sum(1 for count in lines.values() if count > 0)
            coverage_percentages.append((covered / total * 100) if total > 0 else 0)
        
        # 绘制柱状图
        plt.bar(files, coverage_percentages)
        plt.xlabel('Files')
        plt.ylabel('Coverage (%)')
        plt.title('Test Coverage Report')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # 保存图表为base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        return f"data:image/png;base64,{image_base64}"