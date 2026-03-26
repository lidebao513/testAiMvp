const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const cors = require('cors');
const app = express();
const port = 3009;

app.use(bodyParser.json());
app.use(cors());

// 配置信息
const config = {
  mockServices: {
    // 存储Mock服务配置
  }
};

// 存储Mock服务实例
const mockServers = {};

// 存储请求历史
const requestHistory = {};

// 创建Mock服务
const createMockServer = (serviceConfig) => {
  const mockApp = express();
  mockApp.use(bodyParser.json());
  mockApp.use(cors());

  // 注册Mock规则
  serviceConfig.rules.forEach(rule => {
    const { method, path, response, status } = rule;
    
    mockApp[method.toLowerCase()](path, (req, res) => {
      // 记录请求
      if (!requestHistory[serviceConfig.name]) {
        requestHistory[serviceConfig.name] = [];
      }
      
      requestHistory[serviceConfig.name].push({
        timestamp: new Date(),
        method: req.method,
        path: req.path,
        headers: req.headers,
        body: req.body,
        response: response,
        status: status
      });

      // 模拟延迟
      if (rule.delay) {
        setTimeout(() => {
          res.status(status || 200).json(response);
        }, rule.delay);
      } else {
        res.status(status || 200).json(response);
      }
    });
  });

  // 404处理
  mockApp.use('*', (req, res) => {
    res.status(404).json({ message: 'Not Found' });
  });

  return mockApp;
};

// 启动Mock服务
const startMockServer = (serviceName) => {
  const serviceConfig = config.mockServices[serviceName];
  if (!serviceConfig) {
    throw new Error(`Mock服务 ${serviceName} 不存在`);
  }

  if (mockServers[serviceName]) {
    throw new Error(`Mock服务 ${serviceName} 已经在运行`);
  }

  const mockApp = createMockServer(serviceConfig);
  const server = mockApp.listen(serviceConfig.port, () => {
    console.log(`Mock服务 ${serviceName} 运行在 http://localhost:${serviceConfig.port}`);
  });

  mockServers[serviceName] = server;
  return server;
};

// 停止Mock服务
const stopMockServer = (serviceName) => {
  if (!mockServers[serviceName]) {
    throw new Error(`Mock服务 ${serviceName} 没有运行`);
  }

  mockServers[serviceName].close();
  delete mockServers[serviceName];
  console.log(`Mock服务 ${serviceName} 已停止`);
};

// 创建Mock服务
app.post('/services', (req, res) => {
  const { name, port, rules } = req.body;

  if (!name || !port || !rules || !Array.isArray(rules)) {
    return res.status(400).send({ message: '缺少必要参数: name, port, rules' });
  }

  // 检查服务是否已存在
  if (config.mockServices[name]) {
    return res.status(400).send({ message: `Mock服务 ${name} 已存在` });
  }

  // 检查端口是否已被占用
  for (const [serviceName, serviceConfig] of Object.entries(config.mockServices)) {
    if (serviceConfig.port === port) {
      return res.status(400).send({ message: `端口 ${port} 已被使用` });
    }
  }

  // 创建服务配置
  config.mockServices[name] = {
    name,
    port,
    rules
  };

  res.status(200).send({ message: `Mock服务 ${name} 已创建`, service: config.mockServices[name] });
});

// 启动Mock服务
app.post('/services/:name/start', (req, res) => {
  const serviceName = req.params.name;

  try {
    startMockServer(serviceName);
    res.status(200).send({ message: `Mock服务 ${serviceName} 已启动` });
  } catch (error) {
    res.status(400).send({ message: error.message });
  }
});

// 停止Mock服务
app.post('/services/:name/stop', (req, res) => {
  const serviceName = req.params.name;

  try {
    stopMockServer(serviceName);
    res.status(200).send({ message: `Mock服务 ${serviceName} 已停止` });
  } catch (error) {
    res.status(400).send({ message: error.message });
  }
});

// 更新Mock服务
app.put('/services/:name', (req, res) => {
  const serviceName = req.params.name;
  const { port, rules } = req.body;

  if (!config.mockServices[serviceName]) {
    return res.status(404).send({ message: `Mock服务 ${serviceName} 不存在` });
  }

  // 检查端口是否已被占用（排除当前服务）
  if (port) {
    for (const [name, serviceConfig] of Object.entries(config.mockServices)) {
      if (name !== serviceName && serviceConfig.port === port) {
        return res.status(400).send({ message: `端口 ${port} 已被使用` });
      }
    }
  }

  // 更新服务配置
  config.mockServices[serviceName] = {
    ...config.mockServices[serviceName],
    ...(port && { port }),
    ...(rules && { rules })
  };

  // 如果服务正在运行，重启它
  if (mockServers[serviceName]) {
    stopMockServer(serviceName);
    startMockServer(serviceName);
  }

  res.status(200).send({ message: `Mock服务 ${serviceName} 已更新`, service: config.mockServices[serviceName] });
});

// 删除Mock服务
app.delete('/services/:name', (req, res) => {
  const serviceName = req.params.name;

  if (!config.mockServices[serviceName]) {
    return res.status(404).send({ message: `Mock服务 ${serviceName} 不存在` });
  }

  // 如果服务正在运行，停止它
  if (mockServers[serviceName]) {
    stopMockServer(serviceName);
  }

  // 删除服务配置
  delete config.mockServices[serviceName];
  delete requestHistory[serviceName];

  res.status(200).send({ message: `Mock服务 ${serviceName} 已删除` });
});

// 获取所有Mock服务
app.get('/services', (req, res) => {
  const services = Object.entries(config.mockServices).map(([name, service]) => ({
    ...service,
    running: !!mockServers[name]
  }));

  res.status(200).send({ services });
});

// 获取Mock服务详情
app.get('/services/:name', (req, res) => {
  const serviceName = req.params.name;
  const service = config.mockServices[serviceName];

  if (!service) {
    return res.status(404).send({ message: `Mock服务 ${serviceName} 不存在` });
  }

  res.status(200).send({
    ...service,
    running: !!mockServers[serviceName]
  });
});

// 获取Mock服务请求历史
app.get('/services/:name/history', (req, res) => {
  const serviceName = req.params.name;

  if (!config.mockServices[serviceName]) {
    return res.status(404).send({ message: `Mock服务 ${serviceName} 不存在` });
  }

  res.status(200).send({
    history: requestHistory[serviceName] || []
  });
});

// 清空Mock服务请求历史
app.delete('/services/:name/history', (req, res) => {
  const serviceName = req.params.name;

  if (!config.mockServices[serviceName]) {
    return res.status(404).send({ message: `Mock服务 ${serviceName} 不存在` });
  }

  requestHistory[serviceName] = [];
  res.status(200).send({ message: `Mock服务 ${serviceName} 的请求历史已清空` });
});

// 导入Mock服务配置
app.post('/import', (req, res) => {
  const { services } = req.body;

  if (!services || !Array.isArray(services)) {
    return res.status(400).send({ message: '缺少必要参数: services' });
  }

  let importedCount = 0;
  for (const service of services) {
    const { name, port, rules } = service;

    if (name && port && rules && Array.isArray(rules)) {
      // 检查服务是否已存在
      if (!config.mockServices[name]) {
        config.mockServices[name] = service;
        importedCount++;
      }
    }
  }

  res.status(200).send({ message: `成功导入 ${importedCount} 个Mock服务` });
});

// 导出Mock服务配置
app.get('/export', (req, res) => {
  const services = Object.values(config.mockServices);
  res.status(200).send({ services });
});

app.listen(port, () => {
  console.log(`Service Virtualization MCP 服务运行在 http://localhost:${port}`);
  console.log('创建Mock服务地址: POST http://localhost:${port}/services');
  console.log('启动Mock服务地址: POST http://localhost:${port}/services/:name/start');
  console.log('停止Mock服务地址: POST http://localhost:${port}/services/:name/stop');
  console.log('更新Mock服务地址: PUT http://localhost:${port}/services/:name');
  console.log('删除Mock服务地址: DELETE http://localhost:${port}/services/:name');
  console.log('获取所有Mock服务地址: GET http://localhost:${port}/services');
  console.log('获取Mock服务详情地址: GET http://localhost:${port}/services/:name');
  console.log('获取Mock服务请求历史地址: GET http://localhost:${port}/services/:name/history');
  console.log('清空Mock服务请求历史地址: DELETE http://localhost:${port}/services/:name/history');
  console.log('导入Mock服务配置地址: POST http://localhost:${port}/import');
  console.log('导出Mock服务配置地址: GET http://localhost:${port}/export');
});

module.exports = app;