const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const app = express();
const port = 3001;

app.use(bodyParser.json());

// 配置信息
const config = {
  generatorServiceUrl: 'http://localhost:8001/api/generate',
  webhookSecret: 'your-secret-key' // 在Git配置中设置的密钥
};

// 处理Git webhook事件
app.post('/webhook', (req, res) => {
  // 验证webhook密钥
  const secret = req.headers['x-hub-signature'];
  if (!secret) {
    return res.status(401).send('Unauthorized');
  }

  // 解析Git提交信息
  const payload = req.body;
  const repository = payload.repository;
  const commits = payload.commits;
  const branch = payload.ref.split('/').pop();

  console.log(`收到来自 ${repository.name} 仓库的代码提交，分支: ${branch}`);
  console.log(`共 ${commits.length} 个提交`);

  // 提取修改的文件
  const modifiedFiles = [];
  commits.forEach(commit => {
    modifiedFiles.push(...commit.added);
    modifiedFiles.push(...commit.modified);
  });

  console.log('修改的文件:', modifiedFiles);

  // 过滤出需要测试的文件（根据文件类型）
  const testableFiles = modifiedFiles.filter(file => {
    return file.endsWith('.js') || 
           file.endsWith('.ts') || 
           file.endsWith('.py') || 
           file.endsWith('.java') ||
           file.endsWith('.c') ||
           file.endsWith('.cpp');
  });

  if (testableFiles.length > 0) {
    console.log('需要测试的文件:', testableFiles);

    // 调用测试生成服务
    axios.post(config.generatorServiceUrl, {
      repository: repository.name,
      branch: branch,
      files: testableFiles,
      commitMessage: commits[0].message
    })
    .then(response => {
      console.log('测试生成服务响应:', response.data);
      res.status(200).send('测试生成已触发');
    })
    .catch(error => {
      console.error('调用测试生成服务失败:', error);
      res.status(500).send('测试生成触发失败');
    });
  } else {
    console.log('没有需要测试的文件');
    res.status(200).send('没有需要测试的文件');
  }
});

app.listen(port, () => {
  console.log(`Git MCP 服务运行在 http://localhost:${port}`);
  console.log('Webhook 地址: http://localhost:${port}/webhook');
});

module.exports = app;