import React, { useState, useEffect, useRef } from 'react'
import { Card, Row, Col, Table, Button, Modal, Timeline, Statistic } from 'antd'
import * as echarts from 'echarts'

interface ExecutionLog {
  id: string
  testName: string
  status: string
  duration: number
  timestamp: string
  errorMessage?: string
  screenshot?: string
}

const ExecutionMonitoring: React.FC = () => {
  const [executionLogs, setExecutionLogs] = useState<ExecutionLog[]>([
    {
      id: '1',
      testName: '用户登录测试',
      status: '成功',
      duration: 2.5,
      timestamp: '2026-03-26 10:00:00'
    },
    {
      id: '2',
      testName: '商品列表测试',
      status: '失败',
      duration: 1.8,
      timestamp: '2026-03-26 10:01:00',
      errorMessage: 'AssertionError: Expected 200, got 404',
      screenshot: 'https://via.placeholder.com/800x600?text=商品列表测试失败截图'
    },
    {
      id: '3',
      testName: '购物车测试',
      status: '成功',
      duration: 3.2,
      timestamp: '2026-03-26 10:02:00'
    },
    {
      id: '4',
      testName: '支付测试',
      status: '成功',
      duration: 4.5,
      timestamp: '2026-03-26 10:03:00'
    },
    {
      id: '5',
      testName: '订单测试',
      status: '失败',
      duration: 2.1,
      timestamp: '2026-03-26 10:04:00',
      errorMessage: 'TimeoutError: Page timed out after 30 seconds',
      screenshot: 'https://via.placeholder.com/800x600?text=订单测试失败截图'
    }
  ])

  const [selectedLog, setSelectedLog] = useState<ExecutionLog | null>(null)
  const [isScreenshotModalVisible, setIsScreenshotModalVisible] = useState(false)
  const durationRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // 初始化执行时长分布图表
    if (durationRef.current) {
      const durationChart = echarts.init(durationRef.current)
      const durationOption = {
        title: {
          text: '执行时长分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: executionLogs.map(log => log.testName)
        },
        yAxis: {
          type: 'value',
          name: '时长 (秒)'
        },
        series: [{
          data: executionLogs.map(log => log.duration),
          type: 'bar',
          itemStyle: {
            color: function(params) {
              return executionLogs[params.dataIndex].status === '成功' ? '#52c41a' : '#ff4d4f'
            }
          }
        }]
      }
      durationChart.setOption(durationOption)

      // 响应式调整
      window.addEventListener('resize', () => {
        durationChart.resize()
      })
    }
  }, [executionLogs])

  const handleViewScreenshot = (log: ExecutionLog) => {
    setSelectedLog(log)
    setIsScreenshotModalVisible(true)
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id'
    },
    {
      title: '测试名称',
      dataIndex: 'testName',
      key: 'testName'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <span style={{ 
          color: status === '成功' ? '#52c41a' : '#ff4d4f',
          fontWeight: 'bold'
        }}>
          {status}
        </span>
      )
    },
    {
      title: '执行时长 (秒)',
      dataIndex: 'duration',
      key: 'duration'
    },
    {
      title: '执行时间',
      dataIndex: 'timestamp',
      key: 'timestamp'
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <div>
          {record.status === '失败' && record.screenshot && (
            <Button onClick={() => handleViewScreenshot(record)}>
              查看截图
            </Button>
          )}
        </div>
      )
    }
  ]

  const successCount = executionLogs.filter(log => log.status === '成功').length
  const failureCount = executionLogs.filter(log => log.status === '失败').length
  const totalDuration = executionLogs.reduce((sum, log) => sum + log.duration, 0)

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>智能执行监控</h1>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic title="成功用例" value={successCount} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="失败用例" value={failureCount} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="总执行时长" value={totalDuration.toFixed(2)} suffix="秒" />
          </Card>
        </Col>
      </Row>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title="实时执行日志">
            <Timeline>
              {executionLogs.map(log => (
                <Timeline.Item 
                  key={log.id}
                  color={log.status === '成功' ? 'green' : 'red'}
                >
                  <div>
                    <strong>{log.testName}</strong> - {log.status}
                    <br />
                    <small>{log.timestamp} - {log.duration}秒</small>
                    {log.errorMessage && (
                      <div style={{ color: 'red', marginTop: 8, fontSize: '12px' }}>
                        错误: {log.errorMessage}
                      </div>
                    )}
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="执行时长分布">
            <div ref={durationRef} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>
      <Card title="执行详情">
        <Table 
          dataSource={executionLogs} 
          columns={columns} 
          rowKey="id"
        />
      </Card>

      {/* 截图预览模态框 */}
      <Modal
        title={`${selectedLog?.testName} - 失败截图`}
        open={isScreenshotModalVisible}
        onCancel={() => setIsScreenshotModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setIsScreenshotModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={900}
      >
        {selectedLog?.screenshot && (
          <div>
            <img 
              src={selectedLog.screenshot} 
              alt="测试失败截图" 
              style={{ width: '100%', maxHeight: 600, objectFit: 'contain' }}
            />
            {selectedLog.errorMessage && (
              <div style={{ marginTop: 16, padding: 16, backgroundColor: '#fff2f0', borderRadius: 4 }}>
                <strong>错误信息:</strong>
                <p>{selectedLog.errorMessage}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}

export default ExecutionMonitoring