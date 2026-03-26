const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const app = express();
const port = 3004;

app.use(bodyParser.json());

// 配置信息
const config = {
  slackWebhookUrl: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK_URL',
  executorServiceUrl: 'http://localhost:8002/api/execute'
};

// 发送Slack通知
const sendSlackNotification = (message) => {
  return axios.post(config.slackWebhookUrl, {
    text: message
  });
};

// 格式化测试结果通知
const formatTestResultNotification = (testResults) => {
  const { total, passed, failed, duration } = testResults;
  const passRate = total > 0 ? (passed / total * 100).toFixed(2) : 0;

  let message = `*测试执行结果*\n`;
  message += `• 总测试用例: ${total}\n`;
  message += `• 通过: ${passed}\n`;
  message += `• 失败: ${failed}\n`;
  message += `• 通过率: ${passRate}%\n`;
  message += `• 总执行时间: ${duration.toFixed(2)}秒\n`;

  if (failed > 0) {
    message += `\n*失败用例:*\n`;
    testResults.failedTests.forEach(test => {
      message += `• ${test.name}: ${test.error}\n`;
    });
  }

  return message;
};

// 处理测试执行完成事件
app.post('/test-complete', (req, res) => {
  const testResults = req.body;

  console.log('收到测试执行完成事件');
  console.log('测试结果:', testResults);

  // 格式化通知消息
  const notificationMessage = formatTestResultNotification(testResults);

  // 发送Slack通知
  sendSlackNotification(notificationMessage)
    .then(response => {
      console.log('Slack通知已发送');
      res.status(200).send('Slack通知已发送');
    })
    .catch(error => {
      console.error('发送Slack通知失败:', error);
      res.status(500).send('发送Slack通知失败');
    });
});

// 处理构建完成事件
app.post('/build-complete', (req, res) => {
  const buildInfo = req.body;

  console.log('收到构建完成事件');
  console.log('构建信息:', buildInfo);

  // 格式化通知消息
  let message = `*构建完成通知*\n`;
  message += `• 任务名称: ${buildInfo.jobName}\n`;
  message += `• 构建编号: ${buildInfo.buildNumber}\n`;
  message += `• 构建状态: ${buildInfo.status}\n`;
  message += `• 构建时间: ${buildInfo.duration.toFixed(2)}秒\n`;
  message += `• 构建URL: ${buildInfo.url || 'N/A'}\n`;

  // 发送Slack通知
  sendSlackNotification(message)
    .then(response => {
      console.log('Slack通知已发送');
      res.status(200).send('Slack通知已发送');
    })
    .catch(error => {
      console.error('发送Slack通知失败:', error);
      res.status(500).send('发送Slack通知失败');
    });
});

// 处理缺陷创建事件
app.post('/defect-created', (req, res) => {
  const defectInfo = req.body;

  console.log('收到缺陷创建事件');
  console.log('缺陷信息:', defectInfo);

  // 格式化通知消息
  let message = `*新缺陷创建通知*\n`;
  message += `• 缺陷ID: ${defectInfo.id}\n`;
  message += `• 缺陷标题: ${defectInfo.title}\n`;
  message += `• 严重程度: ${defectInfo.severity}\n`;
  message += `• 状态: ${defectInfo.status}\n`;
  message += `• 描述: ${defectInfo.description || '无'}\n`;

  // 发送Slack通知
  sendSlackNotification(message)
    .then(response => {
      console.log('Slack通知已发送');
      res.status(200).send('Slack通知已发送');
    })
    .catch(error => {
      console.error('发送Slack通知失败:', error);
      res.status(500).send('发送Slack通知失败');
    });
});

app.listen(port, () => {
  console.log(`Slack MCP 服务运行在 http://localhost:${port}`);
  console.log('测试完成通知地址: http://localhost:${port}/test-complete');
  console.log('构建完成通知地址: http://localhost:${port}/build-complete');
  console.log('缺陷创建通知地址: http://localhost:${port}/defect-created');
});

module.exports = app;