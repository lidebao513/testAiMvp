import urllib.request
import json

try:
    # 测试根路径
    response = urllib.request.urlopen('http://127.0.0.1:8006/')
    data = response.read().decode('utf-8')
    print('Root path response:', data)
    
    # 测试健康检查路径
    response = urllib.request.urlopen('http://127.0.0.1:8006/health')
    data = response.read().decode('utf-8')
    print('Health check response:', data)
    
    print('API tests passed!')
except Exception as e:
    print(f'Error: {str(e)}')