import sys
import os

# 打印Python版本和路径
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

# 检查是否在虚拟环境中
print(f"Virtual environment: {os.environ.get('VIRTUAL_ENV', 'Not in virtual env')}")

# 尝试导入模块
try:
    import fastapi
    print("✓ fastapi imported successfully")
except ImportError as e:
    print(f"✗ fastapi import failed: {e}")

try:
    import pytest
    print("✓ pytest imported successfully")
except ImportError as e:
    print(f"✗ pytest import failed: {e}")

try:
    import pytest_mock
    print("✓ pytest_mock imported successfully")
except ImportError as e:
    print(f"✗ pytest_mock import failed: {e}")

try:
    from app.core.knowledge_base import KnowledgeBase
    print("✓ KnowledgeBase imported successfully")
except ImportError as e:
    print(f"✗ KnowledgeBase import failed: {e}")