const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const k8s = require('@kubernetes/client-node');
const app = express();
const port = 3007;

app.use(bodyParser.json());

// 配置信息
const config = {
  namespace: 'test',
  testPodTemplate: {
    metadata: {
      name: 'test-pod'
    },
    spec: {
      containers: [
        {
          name: 'test-runner',
          image: 'node:14',
          command: ['sleep', '3600'],
          resources: {
            requests: {
              cpu: '100m',
              memory: '256Mi'
            },
            limits: {
              cpu: '500m',
              memory: '512Mi'
            }
          }
        }
      ],
      restartPolicy: 'Never'
    }
  },
  testDeploymentTemplate: {
    metadata: {
      name: 'test-deployment'
    },
    spec: {
      replicas: 3,
      selector: {
        matchLabels: {
          app: 'test'
        }
      },
      template: {
        metadata: {
          labels: {
            app: 'test'
          }
        },
        spec: {
          containers: [
            {
              name: 'test-service',
              image: 'node:14',
              ports: [
                {
                  containerPort: 8080
                }
              ],
              resources: {
                requests: {
                  cpu: '200m',
                  memory: '512Mi'
                },
                limits: {
                  cpu: '1',
                  memory: '1Gi'
                }
              }
            }
          ]
        }
      }
    }
  }
};

// 初始化Kubernetes客户端
const kc = new k8s.KubeConfig();
kc.loadFromDefault();

const k8sApi = kc.makeApiClient(k8s.CoreV1Api);
const k8sAppsApi = kc.makeApiClient(k8s.AppsV1Api);

// 创建命名空间
const createNamespace = async () => {
  try {
    const namespace = {
      metadata: {
        name: config.namespace
      }
    };
    
    try {
      await k8sApi.readNamespace(config.namespace);
      console.log(`命名空间 ${config.namespace} 已存在`);
    } catch (error) {
      await k8sApi.createNamespace(namespace);
      console.log(`命名空间 ${config.namespace} 已创建`);
    }
  } catch (error) {
    console.error('创建命名空间失败:', error);
  }
};

// 部署测试Pod
app.post('/deploy-pod', async (req, res) => {
  try {
    // 确保命名空间存在
    await createNamespace();
    
    const podName = req.body.name || `test-pod-${Date.now()}`;
    const pod = {
      metadata: {
        name: podName,
        namespace: config.namespace
      },
      spec: config.testPodTemplate.spec
    };
    
    const response = await k8sApi.createNamespacedPod(config.namespace, pod);
    console.log(`Pod ${podName} 已部署`);
    res.status(200).send({ message: `Pod ${podName} 已部署`, pod: response.body });
  } catch (error) {
    console.error('部署Pod失败:', error);
    res.status(500).send({ message: '部署Pod失败', error: error.message });
  }
});

// 部署测试Deployment
app.post('/deploy-deployment', async (req, res) => {
  try {
    // 确保命名空间存在
    await createNamespace();
    
    const deploymentName = req.body.name || `test-deployment-${Date.now()}`;
    const replicas = req.body.replicas || 3;
    
    const deployment = {
      metadata: {
        name: deploymentName,
        namespace: config.namespace
      },
      spec: {
        ...config.testDeploymentTemplate.spec,
        replicas: replicas
      }
    };
    
    const response = await k8sAppsApi.createNamespacedDeployment(config.namespace, deployment);
    console.log(`Deployment ${deploymentName} 已部署`);
    res.status(200).send({ message: `Deployment ${deploymentName} 已部署`, deployment: response.body });
  } catch (error) {
    console.error('部署Deployment失败:', error);
    res.status(500).send({ message: '部署Deployment失败', error: error.message });
  }
});

// 缩放Deployment
app.post('/scale-deployment', async (req, res) => {
  try {
    const { name, replicas } = req.body;
    
    if (!name || !replicas) {
      return res.status(400).send({ message: '缺少必要参数: name 和 replicas' });
    }
    
    const deployment = {
      spec: {
        replicas: replicas
      }
    };
    
    const response = await k8sAppsApi.patchNamespacedDeployment(name, config.namespace, deployment);
    console.log(`Deployment ${name} 已缩放到 ${replicas} 个副本`);
    res.status(200).send({ message: `Deployment ${name} 已缩放到 ${replicas} 个副本`, deployment: response.body });
  } catch (error) {
    console.error('缩放Deployment失败:', error);
    res.status(500).send({ message: '缩放Deployment失败', error: error.message });
  }
});

// 删除Pod
app.delete('/pod/:name', async (req, res) => {
  try {
    const podName = req.params.name;
    
    await k8sApi.deleteNamespacedPod(podName, config.namespace);
    console.log(`Pod ${podName} 已删除`);
    res.status(200).send({ message: `Pod ${podName} 已删除` });
  } catch (error) {
    console.error('删除Pod失败:', error);
    res.status(500).send({ message: '删除Pod失败', error: error.message });
  }
});

// 删除Deployment
app.delete('/deployment/:name', async (req, res) => {
  try {
    const deploymentName = req.params.name;
    
    await k8sAppsApi.deleteNamespacedDeployment(deploymentName, config.namespace);
    console.log(`Deployment ${deploymentName} 已删除`);
    res.status(200).send({ message: `Deployment ${deploymentName} 已删除` });
  } catch (error) {
    console.error('删除Deployment失败:', error);
    res.status(500).send({ message: '删除Deployment失败', error: error.message });
  }
});

// 获取集群状态
app.get('/status', async (req, res) => {
  try {
    // 获取Pod列表
    const podsResponse = await k8sApi.listNamespacedPod(config.namespace);
    const pods = podsResponse.body.items.map(pod => ({
      name: pod.metadata.name,
      status: pod.status.phase,
      containers: pod.spec.containers.map(c => c.name),
      node: pod.spec.nodeName
    }));
    
    // 获取Deployment列表
    const deploymentsResponse = await k8sAppsApi.listNamespacedDeployment(config.namespace);
    const deployments = deploymentsResponse.body.items.map(deployment => ({
      name: deployment.metadata.name,
      replicas: deployment.spec.replicas,
      readyReplicas: deployment.status.readyReplicas || 0
    }));
    
    res.status(200).send({ pods, deployments });
  } catch (error) {
    console.error('获取集群状态失败:', error);
    res.status(500).send({ message: '获取集群状态失败', error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Kubernetes MCP 服务运行在 http://localhost:${port}`);
  console.log('部署Pod地址: http://localhost:${port}/deploy-pod');
  console.log('部署Deployment地址: http://localhost:${port}/deploy-deployment');
  console.log('缩放Deployment地址: http://localhost:${port}/scale-deployment');
  console.log('删除Pod地址: http://localhost:${port}/pod/:name');
  console.log('删除Deployment地址: http://localhost:${port}/deployment/:name');
  console.log('获取集群状态地址: http://localhost:${port}/status');
});

module.exports = app;