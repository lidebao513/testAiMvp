const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const app = express();
const port = 3002;

app.use(bodyParser.json());

// 配置信息
const config = {
  jiraApiUrl: 'https://your-jira-instance.atlassian.net/rest/api/2',
  jiraUsername: 'your-jira-username',
  jiraApiToken: 'your-jira-api-token',
  analyticsServiceUrl: 'http://localhost:8003/api/analyze',
  knowledgeServiceUrl: 'http://localhost:8005/api/knowledge'
};

// 处理Jira webhook事件
app.post('/webhook', (req, res) => {
  const payload = req.body;
  const issue = payload.issue;
  const eventType = payload.webhookEvent;

  console.log(`收到Jira事件: ${eventType}`);
  console.log(`缺陷ID: ${issue.key}`);
  console.log(`缺陷标题: ${issue.fields.summary}`);
  console.log(`缺陷状态: ${issue.fields.status.name}`);
  console.log(`缺陷描述: ${issue.fields.description}`);

  // 处理缺陷创建或更新事件
  if (eventType === 'jira:issue_created' || eventType === 'jira:issue_updated') {
    // 提取缺陷信息
    const defectInfo = {
      id: issue.key,
      title: issue.fields.summary,
      description: issue.fields.description,
      status: issue.fields.status.name,
      severity: issue.fields.priority ? issue.fields.priority.name : '未设置',
      assignee: issue.fields.assignee ? issue.fields.assignee.displayName : '未分配',
      createdAt: issue.fields.created,
      updatedAt: issue.fields.updated
    };

    // 调用分析服务，分析缺陷与测试的关联
    axios.post(config.analyticsServiceUrl + '/defect-analysis', defectInfo)
      .then(response => {
        console.log('缺陷分析结果:', response.data);

        // 调用知识库服务，存储缺陷信息
        return axios.post(config.knowledgeServiceUrl + '/defects', defectInfo);
      })
      .then(response => {
        console.log('缺陷信息已存储到知识库');
        res.status(200).send('缺陷信息已处理');
      })
      .catch(error => {
        console.error('处理缺陷信息失败:', error);
        res.status(500).send('处理缺陷信息失败');
      });
  } else {
    res.status(200).send('事件类型不处理');
  }
});

// 同步Jira缺陷到测试系统
app.get('/sync-defects', (req, res) => {
  // 从Jira获取缺陷列表
  axios.get(config.jiraApiUrl + '/search', {
    auth: {
      username: config.jiraUsername,
      password: config.jiraApiToken
    },
    params: {
      jql: 'project = "YOUR_PROJECT" AND issuetype = Bug ORDER BY created DESC',
      maxResults: 50
    }
  })
  .then(response => {
    const issues = response.data.issues;
    console.log(`从Jira获取到 ${issues.length} 个缺陷`);

    // 处理每个缺陷
    const defectPromises = issues.map(issue => {
      const defectInfo = {
        id: issue.key,
        title: issue.fields.summary,
        description: issue.fields.description,
        status: issue.fields.status.name,
        severity: issue.fields.priority ? issue.fields.priority.name : '未设置',
        assignee: issue.fields.assignee ? issue.fields.assignee.displayName : '未分配',
        createdAt: issue.fields.created,
        updatedAt: issue.fields.updated
      };

      // 存储到知识库
      return axios.post(config.knowledgeServiceUrl + '/defects', defectInfo);
    });

    return Promise.all(defectPromises);
  })
  .then(results => {
    console.log(`成功同步 ${results.length} 个缺陷`);
    res.status(200).send({ message: `成功同步 ${results.length} 个缺陷` });
  })
  .catch(error => {
    console.error('同步缺陷失败:', error);
    res.status(500).send('同步缺陷失败');
  });
});

app.listen(port, () => {
  console.log(`Jira MCP 服务运行在 http://localhost:${port}`);
  console.log('Webhook 地址: http://localhost:${port}/webhook');
  console.log('同步缺陷地址: http://localhost:${port}/sync-defects');
});

module.exports = app;