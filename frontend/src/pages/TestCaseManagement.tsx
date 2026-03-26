import React, { useState } from 'react'
import { Card, Table, Button, Rate, Modal, Input, Select, message } from 'antd'
import { EditOutlined, EyeOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons'

const { TextArea } = Input
const { Option } = Select

interface TestCase {
  id: string
  title: string
  type: string
  status: string
  quality: number
  content: string
  generatedAt: string
}

const TestCaseManagement: React.FC = () => {
  const [testCases, setTestCases] = useState<TestCase[]>([
    {
      id: '1',
      title: '用户登录测试',
      type: 'E2E',
      status: '待审核',
      quality: 0,
      content: 'const { test, expect } = require(\'@playwright/test\');\n\ntest(\'用户登录测试\', async ({ page }) => {\n  await page.goto(\'http://localhost:3000/login\');\n  await page.fill(\'#username\', \'testuser\');\n  await page.fill(\'#password\', \'password123\');\n  await page.click(\'#login-button\');\n  await expect(page).toHaveURL(\'http://localhost:3000/home\');\n});',
      generatedAt: '2026-03-26 10:00:00'
    },
    {
      id: '2',
      title: '添加商品到购物车',
      type: 'API',
      status: '已通过',
      quality: 5,
      content: 'import requests\n\ndef test_add_to_cart():\n    response = requests.post(\'http://localhost:8000/api/cart/add\', json={\n        \'product_id\': 1,\n        \'quantity\': 2\n    })\n    assert response.status_code == 200\n    assert response.json()[\'status\'] == \'success\'',
      generatedAt: '2026-03-26 09:30:00'
    },
    {
      id: '3',
      title: '计算函数测试',
      type: '单元',
      status: '需改进',
      quality: 3,
      content: 'import pytest\n\ndef test_add():\n    assert add(1, 2) == 3\n    assert add(0, 0) == 0\n    assert add(-1, -2) == -3',
      generatedAt: '2026-03-26 09:00:00'
    }
  ])

  const [selectedTestCase, setSelectedTestCase] = useState<TestCase | null>(null)
  const [isPreviewModalVisible, setIsPreviewModalVisible] = useState(false)
  const [isEditModalVisible, setIsEditModalVisible] = useState(false)
  const [editingContent, setEditingContent] = useState('')

  const handlePreview = (testCase: TestCase) => {
    setSelectedTestCase(testCase)
    setIsPreviewModalVisible(true)
  }

  const handleEdit = (testCase: TestCase) => {
    setSelectedTestCase(testCase)
    setEditingContent(testCase.content)
    setIsEditModalVisible(true)
  }

  const handleSaveEdit = () => {
    if (selectedTestCase) {
      setTestCases(prev => prev.map(tc => 
        tc.id === selectedTestCase.id 
          ? { ...tc, content: editingContent } 
          : tc
      ))
      setIsEditModalVisible(false)
      message.success('测试用例已更新')
    }
  }

  const handleQualityChange = (testCase: TestCase, value: number) => {
    setTestCases(prev => prev.map(tc => 
      tc.id === testCase.id 
        ? { ...tc, quality: value, status: value >= 4 ? '已通过' : value >= 2 ? '需改进' : '未通过' }
        : tc
    ))
    message.success('质量评分已更新')
  }

  const columns = [
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
      title: '类型',
      dataIndex: 'type',
      key: 'type'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status'
    },
    {
      title: '质量',
      dataIndex: 'quality',
      key: 'quality',
      render: (_, record) => (
        <Rate 
          count={5} 
          value={record.quality} 
          onChange={(value) => handleQualityChange(record, value)}
        />
      )
    },
    {
      title: '生成时间',
      dataIndex: 'generatedAt',
      key: 'generatedAt'
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <div>
          <Button 
            icon={<EyeOutlined />} 
            style={{ marginRight: 8 }} 
            onClick={() => handlePreview(record)}
          >
            预览
          </Button>
          <Button 
            icon={<EditOutlined />} 
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
        </div>
      )
    }
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>AI生成测试用例管理</h1>
      <Card>
        <Table 
          dataSource={testCases} 
          columns={columns} 
          rowKey="id"
        />
      </Card>

      {/* 预览模态框 */}
      <Modal
        title={selectedTestCase?.title}
        open={isPreviewModalVisible}
        onCancel={() => setIsPreviewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setIsPreviewModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        <div>
          <p><strong>类型:</strong> {selectedTestCase?.type}</p>
          <p><strong>状态:</strong> {selectedTestCase?.status}</p>
          <p><strong>质量:</strong> <Rate count={5} value={selectedTestCase?.quality} disabled /></p>
          <p><strong>生成时间:</strong> {selectedTestCase?.generatedAt}</p>
          <p><strong>内容:</strong></p>
          <pre style={{ backgroundColor: '#f5f5f5', padding: 16, borderRadius: 4, overflow: 'auto' }}>
            {selectedTestCase?.content}
          </pre>
        </div>
      </Modal>

      {/* 编辑模态框 */}
      <Modal
        title={`编辑测试用例: ${selectedTestCase?.title}`}
        open={isEditModalVisible}
        onCancel={() => setIsEditModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setIsEditModalVisible(false)}>
            取消
          </Button>,
          <Button key="save" type="primary" onClick={handleSaveEdit}>
            保存
          </Button>
        ]}
        width={800}
      >
        <TextArea 
          value={editingContent} 
          onChange={(e) => setEditingContent(e.target.value)}
          rows={10}
          style={{ fontFamily: 'monospace' }}
        />
      </Modal>
    </div>
  )
}

export default TestCaseManagement