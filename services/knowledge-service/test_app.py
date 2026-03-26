import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app
    print("App imported successfully!")
    print(f"App title: {app.title}")
    print(f"App description: {app.description}")
    print("Test passed!")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()