const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const app = express();
const port = 3003;

app.use(bodyParser.json());

// 配置信息
const config = {
  jenkinsUrl: 'http://localhost:8080',
  jenkinsUsername: 'admin',
  jenkinsPassword: 'admin',
  executorServiceUrl: 'http://localhost:8002/api/execute',
  generatorServiceUrl: 'http://localhost:8001/api/generate'
};

// 处理Jenkins webhook事件
app.post('/webhook', (req, res) => {
  const payload = req.body;
  const build = payload.build;
  const job = payload.job;

  console.log(`收到Jenkins事件: ${build.status}`);
  console.log(`构建ID: ${build.number}`);
  console.log(`任务名称: ${job.name}`);
  console.log(`构建状态: ${build.status}`);

  // 处理构建完成事件
  if (build.status === 'SUCCESS' || build.status === 'FAILURE') {
    // 提取构建信息
    const buildInfo = {
      jobName: job.name,
      buildNumber: build.number,
      status: build.status,
      timestamp: build.timestamp,
      duration: build.duration
    };

    console.log('构建信息:', buildInfo);

    // 根据构建状态执行不同操作
    if (build.status === 'SUCCESS') {
      // 构建成功，触发测试生成
      axios.post(config.generatorServiceUrl, {
        jobName: job.name,
        buildNumber: build.number,
        trigger: 'jenkins'
      })
      .then(response => {
        console.log('测试生成已触发:', response.data);
        res.status(200).send('测试生成已触发');
      })
      .catch(error => {
        console.error('触发测试生成失败:', error);
        res.status(500).send('触发测试生成失败');
      });
    } else {
      // 构建失败，记录失败信息
      console.log('构建失败，记录失败信息');
      res.status(200).send('构建失败信息已记录');
    }
  } else {
    res.status(200).send('事件类型不处理');
  }
});

// 触发Jenkins构建
app.post('/trigger-build', (req, res) => {
  const { jobName, parameters } = req.body;

  if (!jobName) {
    return res.status(400).send('缺少任务名称');
  }

  // 构建Jenkins API URL
  const jenkinsApiUrl = `${config.jenkinsUrl}/job/${jobName}/build`;

  // 准备请求参数
  const requestConfig = {
    auth: {
      username: config.jenkinsUsername,
      password: config.jenkinsPassword
    },
    headers: {
      'Content-Type': 'application/json'
    }
  };

  // 发送构建请求
  axios.post(jenkinsApiUrl, parameters || {}, requestConfig)
    .then(response => {
      console.log(`已触发Jenkins任务 ${jobName} 的构建`);
      res.status(200).send({ message: `已触发Jenkins任务 ${jobName} 的构建` });
    })
    .catch(error => {
      console.error('触发Jenkins构建失败:', error);
      res.status(500).send('触发Jenkins构建失败');
    });
});

// 获取Jenkins构建状态
app.get('/build-status/:jobName/:buildNumber', (req, res) => {
  const { jobName, buildNumber } = req.params;

  // 构建Jenkins API URL
  const jenkinsApiUrl = `${config.jenkinsUrl}/job/${jobName}/${buildNumber}/api/json`;

  // 准备请求参数
  const requestConfig = {
    auth: {
      username: config.jenkinsUsername,
      password: config.jenkinsPassword
    }
  };

  // 发送请求获取构建状态
  axios.get(jenkinsApiUrl, requestConfig)
    .then(response => {
      const buildStatus = {
        jobName: jobName,
        buildNumber: buildNumber,
        status: response.data.result,
        timestamp: response.data.timestamp,
        duration: response.data.duration,
        url: response.data.url
      };
      res.status(200).send(buildStatus);
    })
    .catch(error => {
      console.error('获取构建状态失败:', error);
      res.status(500).send('获取构建状态失败');
    });
});

app.listen(port, () => {
  console.log(`Jenkins MCP 服务运行在 http://localhost:${port}`);
  console.log('Webhook 地址: http://localhost:${port}/webhook');
  console.log('触发构建地址: http://localhost:${port}/trigger-build');
  console.log('获取构建状态地址: http://localhost:${port}/build-status/:jobName/:buildNumber');
});

module.exports = app;