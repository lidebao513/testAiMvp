const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const app = express();
const port = 3005;

app.use(bodyParser.json());

// 配置信息
const config = {
  allureCommand: 'allure', // 假设allure已安装并添加到PATH
  reportOutputDir: path.join(__dirname, 'allure-results'),
  reportDir: path.join(__dirname, 'allure-report'),
  executorServiceUrl: 'http://localhost:8002/api/execute'
};

// 确保报告目录存在
if (!fs.existsSync(config.reportOutputDir)) {
  fs.mkdirSync(config.reportOutputDir, { recursive: true });
}

if (!fs.existsSync(config.reportDir)) {
  fs.mkdirSync(config.reportDir, { recursive: true });
}

// 生成Allure报告
const generateAllureReport = () => {
  try {
    // 清除旧的报告
    if (fs.existsSync(config.reportDir)) {
      fs.rmSync(config.reportDir, { recursive: true, force: true });
    }
    fs.mkdirSync(config.reportDir, { recursive: true });

    // 生成Allure报告
    console.log('正在生成Allure报告...');
    execSync(`${config.allureCommand} generate ${config.reportOutputDir} -o ${config.reportDir} --clean`);
    console.log('Allure报告已生成');
    return true;
  } catch (error) {
    console.error('生成Allure报告失败:', error);
    return false;
  }
};

// 处理测试执行完成事件，生成Allure报告
app.post('/test-complete', (req, res) => {
  const testResults = req.body;

  console.log('收到测试执行完成事件，准备生成Allure报告');
  console.log('测试结果:', testResults);

  // 生成Allure结果文件
  const timestamp = Date.now();
  const resultFile = path.join(config.reportOutputDir, `result-${timestamp}.json`);

  // 转换测试结果为Allure格式
  const allureResults = testResults.tests.map(test => {
    return {
      uuid: `test-${test.id || timestamp}-${Math.random().toString(36).substr(2, 9)}`,
      historyId: `test-${test.id || timestamp}`,
      testCaseName: test.name,
      fullName: test.name,
      status: test.status === 'success' ? 'passed' : 'failed',
      statusDetails: test.status === 'failed' ? {
        message: test.error,
        trace: test.stack || test.error
      } : {},
      startTime: timestamp,
      stopTime: timestamp + (test.duration || 0) * 1000,
      attachments: test.screenshot ? [{
        name: 'Screenshot',
        type: 'image/png',
        source: test.screenshot
      }] : [],
      labels: [
        { name: 'severity', value: 'normal' },
        { name: 'testType', value: test.type || 'automated' }
      ]
    };
  });

  // 写入Allure结果文件
  try {
    fs.writeFileSync(resultFile, JSON.stringify(allureResults, null, 2));
    console.log('Allure结果文件已写入');

    // 生成Allure报告
    const success = generateAllureReport();

    if (success) {
      res.status(200).send({
        message: 'Allure报告已生成',
        reportUrl: `http://localhost:${port}/report`
      });
    } else {
      res.status(500).send('生成Allure报告失败');
    }
  } catch (error) {
    console.error('写入Allure结果文件失败:', error);
    res.status(500).send('写入Allure结果文件失败');
  }
});

// 提供Allure报告的静态访问
app.use('/report', express.static(config.reportDir));

// 手动触发报告生成
app.get('/generate-report', (req, res) => {
  const success = generateAllureReport();

  if (success) {
    res.status(200).send({
      message: 'Allure报告已生成',
      reportUrl: `http://localhost:${port}/report`
    });
  } else {
    res.status(500).send('生成Allure报告失败');
  }
});

// 清除Allure结果
app.get('/clear-results', (req, res) => {
  try {
    if (fs.existsSync(config.reportOutputDir)) {
      fs.rmSync(config.reportOutputDir, { recursive: true, force: true });
    }
    fs.mkdirSync(config.reportOutputDir, { recursive: true });

    if (fs.existsSync(config.reportDir)) {
      fs.rmSync(config.reportDir, { recursive: true, force: true });
    }
    fs.mkdirSync(config.reportDir, { recursive: true });

    res.status(200).send('Allure结果已清除');
  } catch (error) {
    console.error('清除Allure结果失败:', error);
    res.status(500).send('清除Allure结果失败');
  }
});

app.listen(port, () => {
  console.log(`Allure MCP 服务运行在 http://localhost:${port}`);
  console.log('测试完成报告生成地址: http://localhost:${port}/test-complete');
  console.log('手动生成报告地址: http://localhost:${port}/generate-report');
  console.log('清除结果地址: http://localhost:${port}/clear-results');
  console.log('Allure报告访问地址: http://localhost:${port}/report');
});

module.exports = app;