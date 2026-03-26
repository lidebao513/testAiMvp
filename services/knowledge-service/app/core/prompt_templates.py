# 不同类型的测试生成提示词模板
TEMPLATES = {
    "unit_test": """
    为以下函数生成单元测试，要求：
    - 覆盖正常路径、边界条件、异常情况
    - 使用AAA模式（Arrange-Act-Assert）
    - 包含Mock外部依赖
    函数代码：
    {code}
    """,
    
    "api_test": """
    基于以下API规范生成接口测试用例：
    - 覆盖所有状态码（2xx, 4xx, 5xx）
    - 参数校验测试
    - 业务逻辑测试
    - 安全测试（SQL注入、XSS）
    API规范：
    {api_spec}
    """,
    
    "e2e_test": """
    生成E2E测试脚本，基于以下用户场景：
    - 使用Playwright
    - 包含等待策略
    - 添加断言和截图
    用户场景：
    {user_scenario}
    """
}