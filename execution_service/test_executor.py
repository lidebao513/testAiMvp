from typing import List, Dict, Any, Optional, Tuple
import os
import subprocess
import time
import json
import re
import logging
import datetime
import platform
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestExecutor")

@dataclass
class TestCase:
    """测试用例类"""
    id: str
    name: str
    command: str
    framework: str
    dependencies: List[str] = None
    priority: int = 1
    timeout: int = 60

@dataclass
class TestResult:
    """测试结果类"""
    test_id: str
    status: str  # passed, failed, error, skipped
    duration: float
    output: str
    error: str = ""
    retries: int = 0
    is_environment_issue: bool = False
    screenshot_path: Optional[str] = None

class TestFrameworkAdapter(ABC):
    """测试框架适配器抽象类"""
    
    @abstractmethod
    def run_test(self, test_case: TestCase) -> TestResult:
        """运行测试用例"""
        pass
    
    @abstractmethod
    def parse_output(self, output: str) -> Dict[str, Any]:
        """解析测试输出"""
        pass
    
    @abstractmethod
    def detect_environment_issue(self, error: str) -> bool:
        """检测环境问题"""
        pass

class JestAdapter(TestFrameworkAdapter):
    """Jest测试框架适配器"""
    
    def run_test(self, test_case: TestCase) -> TestResult:
        start_time = time.time()
        result = subprocess.run(
            test_case.command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=test_case.timeout
        )
        duration = time.time() - start_time
        
        status = "passed" if result.returncode == 0 else "failed"
        
        return TestResult(
            test_id=test_case.id,
            status=status,
            duration=duration,
            output=result.stdout,
            error=result.stderr
        )
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        # 简单的Jest输出解析
        passed = re.search(r'PASS\s+(\d+)', output)
        failed = re.search(r'FAIL\s+(\d+)', output)
        
        return {
            "passed": int(passed.group(1)) if passed else 0,
            "failed": int(failed.group(1)) if failed else 0
        }
    
    def detect_environment_issue(self, error: str) -> bool:
        # 检测常见的环境问题
        env_issues = [
            "ENOTFOUND",
            "EACCES",
            "ECONNREFUSED",
            "Timeout",
            "memory limit"
        ]
        
        return any(issue in error for issue in env_issues)

class PytestAdapter(TestFrameworkAdapter):
    """PyTest测试框架适配器"""
    
    def run_test(self, test_case: TestCase) -> TestResult:
        start_time = time.time()
        result = subprocess.run(
            test_case.command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=test_case.timeout
        )
        duration = time.time() - start_time
        
        status = "passed" if result.returncode == 0 else "failed"
        
        return TestResult(
            test_id=test_case.id,
            status=status,
            duration=duration,
            output=result.stdout,
            error=result.stderr
        )
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        # 简单的PyTest输出解析
        passed = re.search(r'(\d+) passed', output)
        failed = re.search(r'(\d+) failed', output)
        
        return {
            "passed": int(passed.group(1)) if passed else 0,
            "failed": int(failed.group(1)) if failed else 0
        }
    
    def detect_environment_issue(self, error: str) -> bool:
        # 检测常见的环境问题
        env_issues = [
            "ImportError",
            "ModuleNotFoundError",
            "ConnectionError",
            "TimeoutError",
            "OSError"
        ]
        
        return any(issue in error for issue in env_issues)

class SeleniumAdapter(TestFrameworkAdapter):
    """Selenium测试框架适配器"""
    
    def run_test(self, test_case: TestCase) -> TestResult:
        start_time = time.time()
        result = subprocess.run(
            test_case.command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=test_case.timeout
        )
        duration = time.time() - start_time
        
        status = "passed" if result.returncode == 0 else "failed"
        
        # 尝试捕获截图（如果存在）
        screenshot_path = None
        screenshots = list(Path(".").glob("*.png"))
        if screenshots:
            screenshot = max(screenshots, key=os.path.getmtime)
            screenshot_path = str(screenshot)
        
        return TestResult(
            test_id=test_case.id,
            status=status,
            duration=duration,
            output=result.stdout,
            error=result.stderr,
            screenshot_path=screenshot_path
        )
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        # 简单的Selenium输出解析
        passed = re.search(r'PASSED', output)
        failed = re.search(r'FAILED', output)
        
        return {
            "passed": 1 if passed else 0,
            "failed": 1 if failed else 0
        }
    
    def detect_environment_issue(self, error: str) -> bool:
        # 检测常见的环境问题
        env_issues = [
            "WebDriverException",
            "SessionNotCreatedException",
            "NoSuchDriverException",
            "TimeoutException",
            "ConnectionRefusedError"
        ]
        
        return any(issue in error for issue in env_issues)

class TestExecutor:
    """智能测试执行引擎"""
    
    def __init__(self):
        """初始化测试执行引擎"""
        self.adapters = {
            "jest": JestAdapter(),
            "pytest": PytestAdapter(),
            "selenium": SeleniumAdapter()
        }
        self.test_results = {}
        self.log_dir = Path("test_logs")
        self.log_dir.mkdir(exist_ok=True)
    
    def analyze_code_changes(self, diff: str) -> List[str]:
        """分析代码变更，确定需要执行的测试
        
        Args:
            diff (str): 代码变更的diff文本
            
        Returns:
            List[str]: 需要执行的测试用例ID列表
        """
        # 简单的代码变更分析逻辑
        # 实际项目中可能需要更复杂的分析，如静态分析、依赖分析等
        affected_files = set()
        
        # 解析diff，提取变更的文件
        lines = diff.split('\n')
        for line in lines:
            if line.startswith('+++ b/') or line.startswith('--- a/'):
                file_path = line.split('/', 1)[1] if '/' in line else line
                affected_files.add(file_path)
        
        # 根据变更的文件，确定需要执行的测试
        # 这里使用简单的映射关系，实际项目中可能需要更复杂的依赖分析
        test_mapping = {
            "src/components/": ["test-1", "test-2"],
            "src/utils/": ["test-3"],
            "src/api/": ["test-4", "test-5"]
        }
        
        tests_to_run = []
        for file_path in affected_files:
            for pattern, tests in test_mapping.items():
                if pattern in file_path:
                    tests_to_run.extend(tests)
        
        return list(set(tests_to_run))
    
    def analyze_test_dependencies(self, tests: List[TestCase]) -> List[TestCase]:
        """分析测试依赖，优化执行顺序
        
        Args:
            tests (List[TestCase]): 测试用例列表
            
        Returns:
            List[TestCase]: 优化执行顺序后的测试用例列表
        """
        # 构建依赖图
        dependency_graph = {test.id: test.dependencies or [] for test in tests}
        
        # 使用拓扑排序确定执行顺序
        visited = set()
        temp = set()
        order = []
        
        def visit(test_id):
            if test_id in temp:
                raise ValueError(f"循环依赖 detected: {test_id}")
            if test_id not in visited:
                temp.add(test_id)
                for dep in dependency_graph.get(test_id, []):
                    visit(dep)
                temp.remove(test_id)
                visited.add(test_id)
                order.append(test_id)
        
        for test in tests:
            if test.id not in visited:
                visit(test.id)
        
        # 根据拓扑排序结果重新排序测试用例
        test_map = {test.id: test for test in tests}
        ordered_tests = [test_map[test_id] for test_id in order]
        
        return ordered_tests
    
    def run_test_with_retry(self, test_case: TestCase, max_retries: int = 3) -> TestResult:
        """运行测试用例，支持自动重试
        
        Args:
            test_case (TestCase): 测试用例
            max_retries (int, optional): 最大重试次数，默认为3
            
        Returns:
            TestResult: 测试结果
        """
        adapter = self.adapters.get(test_case.framework, JestAdapter())
        
        for attempt in range(max_retries + 1):
            result = adapter.run_test(test_case)
            
            if result.status == "passed":
                result.retries = attempt
                return result
            
            # 检测是否是环境问题
            is_env_issue = adapter.detect_environment_issue(result.error)
            result.is_environment_issue = is_env_issue
            
            # 如果是环境问题且还有重试次数，进行重试
            if is_env_issue and attempt < max_retries:
                logger.warning(f"测试 {test_case.id} 因环境问题失败，正在重试 ({attempt + 1}/{max_retries})...")
                time.sleep(2)  # 等待2秒后重试
            else:
                result.retries = attempt
                return result
    
    def collect_logs(self, test_case: TestCase, result: TestResult):
        """收集测试日志
        
        Args:
            test_case (TestCase): 测试用例
            result (TestResult): 测试结果
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"test_{test_case.id}_{timestamp}.log"
        
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Test ID: {test_case.id}\n")
            f.write(f"Test Name: {test_case.name}\n")
            f.write(f"Framework: {test_case.framework}\n")
            f.write(f"Command: {test_case.command}\n")
            f.write(f"Status: {result.status}\n")
            f.write(f"Duration: {result.duration:.2f}s\n")
            f.write(f"Retries: {result.retries}\n")
            f.write(f"Is Environment Issue: {result.is_environment_issue}\n")
            if result.screenshot_path:
                f.write(f"Screenshot: {result.screenshot_path}\n")
            f.write("\nOutput:\n")
            f.write(result.output)
            if result.error:
                f.write("\nError:\n")
                f.write(result.error)
        
        logger.info(f"测试日志已保存到: {log_file}")
    
    def run_tests(self, tests: List[TestCase], code_diff: Optional[str] = None) -> Dict[str, TestResult]:
        """运行测试
        
        Args:
            tests (List[TestCase]): 测试用例列表
            code_diff (Optional[str], optional): 代码变更的diff文本，默认为None
            
        Returns:
            Dict[str, TestResult]: 测试结果字典
        """
        # 如果提供了代码变更，分析需要执行的测试
        if code_diff:
            tests_to_run_ids = self.analyze_code_changes(code_diff)
            tests = [test for test in tests if test.id in tests_to_run_ids]
            logger.info(f"根据代码变更，需要执行 {len(tests)} 个测试")
        
        # 分析测试依赖，优化执行顺序
        tests = self.analyze_test_dependencies(tests)
        logger.info(f"优化后的测试执行顺序: {[test.id for test in tests]}")
        
        # 执行测试
        results = {}
        for test in tests:
            logger.info(f"开始执行测试: {test.id} - {test.name}")
            result = self.run_test_with_retry(test)
            results[test.id] = result
            
            # 收集日志
            self.collect_logs(test, result)
            
            logger.info(f"测试 {test.id} 执行完成，状态: {result.status}, 耗时: {result.duration:.2f}s, 重试次数: {result.retries}")
        
        self.test_results = results
        return results
    
    def generate_report(self, output_path: str):
        """生成测试报告
        
        Args:
            output_path (str): 报告输出路径
        """
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": {
                "total": len(self.test_results),
                "passed": sum(1 for r in self.test_results.values() if r.status == "passed"),
                "failed": sum(1 for r in self.test_results.values() if r.status == "failed"),
                "error": sum(1 for r in self.test_results.values() if r.status == "error"),
                "environment_issues": sum(1 for r in self.test_results.values() if r.is_environment_issue)
            },
            "results": {}
        }
        
        for test_id, result in self.test_results.items():
            report["results"][test_id] = {
                "status": result.status,
                "duration": result.duration,
                "retries": result.retries,
                "is_environment_issue": result.is_environment_issue,
                "screenshot_path": result.screenshot_path
            }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"测试报告已生成: {output_path}")

if __name__ == "__main__":
    # 示例用法
    executor = TestExecutor()
    
    # 定义测试用例
    tests = [
        TestCase(
            id="test-1",
            name="测试组件渲染",
            command="npm test -- -t 'Component rendering'",
            framework="jest",
            dependencies=[],
            priority=1
        ),
        TestCase(
            id="test-2",
            name="测试API调用",
            command="python -m pytest tests/test_api.py -v",
            framework="pytest",
            dependencies=["test-1"],
            priority=2
        ),
        TestCase(
            id="test-3",
            name="测试用户登录",
            command="python tests/test_login.py",
            framework="selenium",
            dependencies=["test-2"],
            priority=3
        )
    ]
    
    # 模拟代码变更
    code_diff = """
--- a/src/components/Button.js
+++ b/src/components/Button.js
@@ -1,5 +1,5 @@
 function Button({ text, onClick }) {
-  return <button>{text}</button>;
+  return <button className="btn">{text}</button>;
 }
 
 export default Button;
 """
    
    # 运行测试
    results = executor.run_tests(tests, code_diff)
    
    # 生成报告
    executor.generate_report("test_report.json")
    
    # 打印结果
    print("\n测试执行结果:")
    for test_id, result in results.items():
        print(f"{test_id}: {result.status} (耗时: {result.duration:.2f}s, 重试: {result.retries})")
