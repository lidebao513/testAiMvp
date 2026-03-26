import React, { useState, useEffect, useRef } from 'react'
import { Card, Row, Col, Input, Button, Table, Modal, Tag } from 'antd'
import * as echarts from 'echarts'

interface TestPattern {
  id: string
  name: string
  category: string
  description: string
  usageCount: number
}

interface Defect {
  id: string
  title: string
  severity: string
  status: string
  description: string
  createdAt: string
}

interface SimilarTestCase {
  id: string
  title: string
  similarity: number
  content: string
}

const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [defects, setDefects] = useState<Defect[]>([
    {
      id: '1',
      title: '登录页面响应慢',
      severity: '高',
      status: '已修复',
      description: '用户登录时页面响应时间超过3秒',
      createdAt: '2026-03-20'
    },
    {
      id: '2',
      title: '购物车数据丢失',
      severity: '中',
      status: '进行中',
      description: '用户刷新页面后购物车数据丢失',
      createdAt: '2026-03-22'
    },
    {
      id: '3',
      title: '支付接口错误',
      severity: '高',
      status: '已修复',
      description: '支付接口返回500错误',
      createdAt: '2026-03-18'
    }
  ])

  const [testPatterns, setTestPatterns] = useState<TestPattern[]>([
    {
      id: '1',
      name: '边界值测试',
      category: '单元测试',
      description: '测试边界条件和极限值',
      usageCount: 120
    },
    {
      id: '2',
      name: 'API接口测试',
      category: '集成测试',
      description: '测试API接口的各种场景',
      usageCount: 95
    },
    {
      id: '3',
      name: '用户流程测试',
      category: 'E2E测试',
      description: '测试完整的用户流程',
      usageCount: 80
    },
    {
      id: '4',
      name: '安全测试',
      category: '安全测试',
      description: '测试系统的安全性',
      usageCount: 65
    }
  ])

  const [similarTestCases, setSimilarTestCases] = useState<SimilarTestCase[]>([
    {
      id: '1',
      title: '用户登录测试',
      similarity: 0.95,
      content: '测试用户登录功能的各种场景'
    },
    {
      id: '2',
      title: '管理员登录测试',
      similarity: 0.85,
      content: '测试管理员登录功能'
    },
    {
      id: '3',
      title: '登录失败测试',
      similarity: 0.75,
      content: '测试登录失败的各种场景'
    }
  ])

  const [selectedDefect, setSelectedDefect] = useState<Defect | null>(null)
  const [isDefectModalVisible, setIsDefectModalVisible] = useState(false)
  const patternRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // 初始化测试模式可视化图表
    if (patternRef.current) {
      const patternChart = echarts.init(patternRef.current)
      const patternOption = {
        title: {
          text: '测试模式使用频率',
          left: 'center'
        },
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [{
          name: '使用频率',
          type: 'pie',
          radius: '50%',
          data: testPatterns.map(pattern => ({
            value: pattern.usageCount,
            name: pattern.name
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      patternChart.setOption(patternOption)

      // 响应式调整
      window.addEventListener('resize', () => {
        patternChart.resize()
      })
    }
  }, [testPatterns])

  const handleSearch = () => {
    // 模拟搜索功能
    console.log('搜索:', searchQuery)
  }

  const handleViewDefect = (defect: Defect) => {
    setSelectedDefect(defect)
    setIsDefectModalVisible(true)
  }

  const defectColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id'
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title'
    },
    {
      title: '严重程度',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity: string) => (
        <Tag color={severity === '高' ? 'red' : severity === '中' ? 'orange' : 'blue'}>
          {severity}
        </Tag>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status'
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt'
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button onClick={() => handleViewDefect(record)}>
          查看
        </Button>
      )
    }
  ]

  const similarTestCaseColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id'
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title'
    },
    {
      title: '相似度',
      dataIndex: 'similarity',
      key: 'similarity',
      render: (similarity: number) => (
        <div>
          <div style={{ width: '100%', height: 8, backgroundColor: '#f0f0f0', borderRadius: 4 }}>
            <div 
              style={{ 
                width: `${similarity * 100}%`, 
                height: '100%', 
                backgroundColor: '#1890ff',
                borderRadius: 4
              }}
            />
          </div>
          <div style={{ marginTop: 4, fontSize: '12px' }}>
            {Math.round(similarity * 100)}%
          </div>
        </div>
      )
    },
    {
      title: '内容',
      dataIndex: 'content',
      key: 'content'
    }
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>知识库管理</h1>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card title="测试模式可视化">
            <div ref={patternRef} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={16}>
          <Card title="历史缺陷检索">
            <div style={{ marginBottom: 16 }}>
              <Input.Search
                placeholder="输入缺陷关键词"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onSearch={handleSearch}
                style={{ width: 300 }}
                enterButton
              />
            </div>
            <Table 
              dataSource={defects} 
              columns={defectColumns} 
              rowKey="id"
              pagination={{ pageSize: 5 }}
            />
          </Card>
        </Col>
      </Row>
      <Card title="相似用例推荐">
        <Table 
          dataSource={similarTestCases} 
          columns={similarTestCaseColumns} 
          rowKey="id"
        />
      </Card>

      {/* 缺陷详情模态框 */}
      <Modal
        title={selectedDefect?.title}
        open={isDefectModalVisible}
        onCancel={() => setIsDefectModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setIsDefectModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        <div>
          <p><strong>严重程度:</strong> <Tag color={selectedDefect?.severity === '高' ? 'red' : selectedDefect?.severity === '中' ? 'orange' : 'blue'}>
            {selectedDefect?.severity}
          </Tag></p>
          <p><strong>状态:</strong> {selectedDefect?.status}</p>
          <p><strong>创建时间:</strong> {selectedDefect?.createdAt}</p>
          <p><strong>描述:</strong></p>
          <p>{selectedDefect?.description}</p>
        </div>
      </Modal>
    </div>
  )
}

export default KnowledgeBase