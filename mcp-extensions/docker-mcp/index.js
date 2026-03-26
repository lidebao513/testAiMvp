const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const Docker = require('dockerode');
const app = express();
const port = 3006;

app.use(bodyParser.json());

// 配置信息
const config = {
  dockerHost: process.env.DOCKER_HOST || 'unix:///var/run/docker.sock',
  testContainers: {
    mysql: {
      image: 'mysql:5.7',
      name: 'test-mysql',
      ports: { '3306/tcp': 3306 },
      env: {
        MYSQL_ROOT_PASSWORD: 'test123',
        MYSQL_DATABASE: 'test_db'
      },
      volumes: ['test-mysql-data:/var/lib/mysql']
    },
    redis: {
      image: 'redis:6.0',
      name: 'test-redis',
      ports: { '6379/tcp': 6379 }
    },
    selenium: {
      image: 'selenium/standalone-chrome:latest',
      name: 'test-selenium',
      ports: { '4444/tcp': 4444 }
    }
  }
};

// 初始化Docker客户端
const docker = new Docker({ socketPath: config.dockerHost });

// 启动容器
const startContainer = async (containerConfig) => {
  try {
    // 检查容器是否存在
    const containers = await docker.listContainers({ all: true });
    const existingContainer = containers.find(c => c.Names.includes(`/${containerConfig.name}`));

    if (existingContainer) {
      // 如果容器存在，启动它
      const container = docker.getContainer(existingContainer.Id);
      await container.start();
      console.log(`容器 ${containerConfig.name} 已启动`);
    } else {
      // 如果容器不存在，创建并启动它
      const container = await docker.createContainer({
        name: containerConfig.name,
        Image: containerConfig.image,
        ExposedPorts: Object.fromEntries(
          Object.keys(containerConfig.ports || {}).map(port => [port, {})  
        ),
        HostConfig: {
          PortBindings: containerConfig.ports || {},
          Binds: containerConfig.volumes || []
        },
        Env: containerConfig.env ? Object.entries(containerConfig.env).map(([k, v]) => `${k}=${v}`) : []
      });
      await container.start();
      console.log(`容器 ${containerConfig.name} 已创建并启动`);
    }
    return true;
  } catch (error) {
    console.error(`启动容器 ${containerConfig.name} 失败:`, error);
    return false;
  }
};

// 停止容器
const stopContainer = async (containerName) => {
  try {
    const containers = await docker.listContainers({ all: true });
    const existingContainer = containers.find(c => c.Names.includes(`/${containerName}`));

    if (existingContainer) {
      const container = docker.getContainer(existingContainer.Id);
      await container.stop();
      console.log(`容器 ${containerName} 已停止`);
      return true;
    } else {
      console.log(`容器 ${containerName} 不存在`);
      return false;
    }
  } catch (error) {
    console.error(`停止容器 ${containerName} 失败:`, error);
    return false;
  }
};

// 启动所有测试容器
app.post('/start-all', async (req, res) => {
  console.log('开始启动所有测试容器');
  
  const results = {};
  for (const [name, config] of Object.entries(config.testContainers)) {
    results[name] = await startContainer(config);
  }
  
  res.status(200).send({ message: '测试容器启动完成', results });
});

// 停止所有测试容器
app.post('/stop-all', async (req, res) => {
  console.log('开始停止所有测试容器');
  
  const results = {};
  for (const [name] of Object.entries(config.testContainers)) {
    results[name] = await stopContainer(name);
  }
  
  res.status(200).send({ message: '测试容器停止完成', results });
});

// 启动指定容器
app.post('/start/:container', async (req, res) => {
  const containerName = req.params.container;
  const containerConfig = config.testContainers[containerName];
  
  if (!containerConfig) {
    return res.status(404).send({ message: '容器配置不存在' });
  }
  
  const success = await startContainer(containerConfig);
  if (success) {
    res.status(200).send({ message: `容器 ${containerName} 启动成功` });
  } else {
    res.status(500).send({ message: `容器 ${containerName} 启动失败` });
  }
});

// 停止指定容器
app.post('/stop/:container', async (req, res) => {
  const containerName = req.params.container;
  
  const success = await stopContainer(containerName);
  if (success) {
    res.status(200).send({ message: `容器 ${containerName} 停止成功` });
  } else {
    res.status(500).send({ message: `容器 ${containerName} 停止失败` });
  }
});

// 获取容器状态
app.get('/status', async (req, res) => {
  try {
    const containers = await docker.listContainers({ all: true });
    const status = {};
    
    for (const [name] of Object.entries(config.testContainers)) {
      const container = containers.find(c => c.Names.includes(`/${name}`));
      if (container) {
        status[name] = {
          status: container.State,
          id: container.Id,
          image: container.Image
        };
      } else {
        status[name] = {
          status: 'not_created'
        };
      }
    }
    
    res.status(200).send(status);
  } catch (error) {
    console.error('获取容器状态失败:', error);
    res.status(500).send({ message: '获取容器状态失败' });
  }
});

app.listen(port, () => {
  console.log(`Docker MCP 服务运行在 http://localhost:${port}`);
  console.log('启动所有容器地址: http://localhost:${port}/start-all');
  console.log('停止所有容器地址: http://localhost:${port}/stop-all');
  console.log('启动指定容器地址: http://localhost:${port}/start/:container');
  console.log('停止指定容器地址: http://localhost:${port}/stop/:container');
  console.log('获取容器状态地址: http://localhost:${port}/status');
});

module.exports = app;