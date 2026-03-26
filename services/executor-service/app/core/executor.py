import asyncio
import subprocess
import docker
from typing import List, Dict, Any

class TestExecutor:
    """测试执行器类，用于执行测试和管理测试环境
    
    该类提供了执行测试的功能，包括单测执行、并行执行、容器化执行和测试分发。
    """
    
    def __init__(self):
        """初始化测试执行器
        
        初始化Docker客户端，用于容器化测试执行。
        """
        # 初始化Docker客户端
        self.client = docker.from_env()
    
    async def run_test(self, test_command: str, test_type: str, environment: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行单个测试
        
        在本地环境中执行单个测试命令，并返回执行结果。
        
        Args:
            test_command (str): 测试命令
            test_type (str): 测试类型
            environment (Dict[str, Any], optional): 环境变量，默认为None
            
        Returns:
            Dict[str, Any]: 测试执行结果，包含状态、输出、错误和返回码
            
        Example:
            >>> executor = TestExecutor()
            >>> result = await executor.run_test("pytest test.py", "unit")
            >>> print(result)
            {
                "status": "passed",
                "output": "...测试输出...",
                "error": "",
                "return_code": 0
            }
        """
        try:
            # 构建测试环境
            env_vars = environment or {}
            
            # 执行测试
            result = subprocess.run(
                test_command, 
                shell=True, 
                capture_output=True, 
                text=True,
                env=env_vars
            )
            
            # 构建返回结果
            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            # 处理异常情况
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_tests_in_parallel(self, tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """并行执行多个测试
        
        并行执行多个测试，提高测试执行效率。
        
        Args:
            tests (List[Dict[str, Any]]): 测试列表，每个测试包含command、type和environment字段
            
        Returns:
            List[Dict[str, Any]]: 测试执行结果列表
            
        Example:
            >>> executor = TestExecutor()
            >>> tests = [
            ...     {"command": "pytest test1.py", "type": "unit"},
            ...     {"command": "pytest test2.py", "type": "unit"}
            ... ]
            >>> results = await executor.run_tests_in_parallel(tests)
            >>> print(results)
            [
                {"status": "passed", "output": "...", "error": "", "return_code": 0},
                {"status": "passed", "output": "...", "error": "", "return_code": 0}
            ]
        """
        # 创建测试任务
        tasks = []
        for test in tests:
            task = self.run_test(
                test_command=test.get("command"),
                test_type=test.get("type"),
                environment=test.get("environment")
            )
            tasks.append(task)
        
        # 并行执行所有测试任务
        return await asyncio.gather(*tasks)
    
    def run_test_in_container(self, test_command: str, image: str, volumes: List[str] = None) -> Dict[str, Any]:
        """在Docker容器中执行测试
        
        在隔离的Docker容器中执行测试，确保测试环境的一致性。
        
        Args:
            test_command (str): 测试命令
            image (str): Docker镜像名称
            volumes (List[str], optional): 挂载卷列表，默认为None
            
        Returns:
            Dict[str, Any]: 测试执行结果，包含状态、输出和返回码
            
        Example:
            >>> executor = TestExecutor()
            >>> result = executor.run_test_in_container(
            ...     "pytest test.py",
            ...     "python:3.9-slim",
            ...     ["/path/to/tests:/app/tests"]
            ... )
            >>> print(result)
            {
                "status": "passed",
                "output": "...测试输出...",
                "return_code": 0
            }
        """
        try:
            # 准备容器配置
            container_volumes = {}
            if volumes:
                for volume in volumes:
                    # 解析卷挂载配置，格式为 "host_path:container_path"
                    host_path, container_path = volume.split(":")
                    container_volumes[host_path] = {
                        "bind": container_path,
                        "mode": "rw"  # 读写模式
                    }
            
            # 运行容器
            container = self.client.containers.run(
                image,
                command=test_command,
                volumes=container_volumes,
                detach=True,  # 后台运行
                remove=True  # 容器完成后自动删除
            )
            
            # 等待容器完成
            result = container.wait()
            logs = container.logs().decode("utf-8")
            
            # 构建返回结果
            return {
                "status": "passed" if result["StatusCode"] == 0 else "failed",
                "output": logs,
                "return_code": result["StatusCode"]
            }
        except Exception as e:
            # 处理异常情况
            return {
                "status": "error",
                "error": str(e)
            }
    
    def distribute_tests(self, tests: List[Dict[str, Any]], nodes: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """将测试分发到多个节点
        
        使用轮询策略将测试分发到多个节点，实现测试的分布式执行。
        
        Args:
            tests (List[Dict[str, Any]]): 测试列表
            nodes (List[str]): 节点列表
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 测试分发结果，键为节点名称，值为分配的测试列表
            
        Example:
            >>> executor = TestExecutor()
            >>> tests = [
            ...     {"command": "pytest test1.py", "type": "unit"},
            ...     {"command": "pytest test2.py", "type": "unit"},
            ...     {"command": "pytest test3.py", "type": "unit"}
            ... ]
            >>> nodes = ["node1", "node2"]
            >>> distribution = executor.distribute_tests(tests, nodes)
            >>> print(distribution)
            {
                "node1": [{"command": "pytest test1.py", "type": "unit"}, {"command": "pytest test3.py", "type": "unit"}],
                "node2": [{"command": "pytest test2.py", "type": "unit"}]
            }
        """
        # 初始化分发结果
        distribution = {node: [] for node in nodes}
        
        # 使用轮询策略分发测试
        for i, test in enumerate(tests):
            node_index = i % len(nodes)  # 计算节点索引
            node = nodes[node_index]  # 获取节点
            distribution[node].append(test)  # 分配测试
        
        return distribution