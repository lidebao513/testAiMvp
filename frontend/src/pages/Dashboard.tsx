import React, { useEffect, useRef } from 'react'
import { Card, Row, Col, Statistic } from 'antd'
import * as echarts from 'echarts'

const Dashboard: React.FC = () => {
  const passRateRef = useRef<HTMLDivElement>(null)
  const coverageRef = useRef<HTMLDivElement>(null)
  const defectRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // 初始化测试通过率趋势图
    if (passRateRef.current) {
      const passRateChart = echarts.init(passRateRef.current)
      const passRateOption = {
        title: {
          text: '测试通过率趋势',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: ['1月', '2月', '3月', '4月', '5月', '6月']
        },
        yAxis: {
          type: 'percent',
          min: 0,
          max: 100
        },
        series: [{
          data: [85, 88, 92, 90, 95, 97],
          type: 'line',
          smooth: true,
          lineStyle: {
            color: '#52c41a'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
              { offset: 1, color: 'rgba(82, 196, 26, 0.1)' }
            ])
          }
        }]
      }
      passRateChart.setOption(passRateOption)

      // 响应式调整
      window.addEventListener('resize', () => {
        passRateChart.resize()
      })
    }

    // 初始化覆盖率变化曲线
    if (coverageRef.current) {
      const coverageChart = echarts.init(coverageRef.current)
      const coverageOption = {
        title: {
          text: '覆盖率变化曲线',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: ['1月', '2月', '3月', '4月', '5月', '6月']
        },
        yAxis: {
          type: 'percent',
          min: 0,
          max: 100
        },
        series: [{
          data: [65, 70, 75, 80, 85, 88],
          type: 'line',
          smooth: true,
          lineStyle: {
            color: '#1890ff'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
              { offset: 1, color: 'rgba(24, 144, 255, 0.1)' }
            ])
          }
        }]
      }
      coverageChart.setOption(coverageOption)

      // 响应式调整
      window.addEventListener('resize', () => {
        coverageChart.resize()
      })
    }

    // 初始化缺陷发现率统计
    if (defectRef.current) {
      const defectChart = echarts.init(defectRef.current)
      const defectOption = {
        title: {
          text: '缺陷发现率统计',
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
          name: '缺陷类型',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 30, name: '功能缺陷' },
            { value: 15, name: '性能问题' },
            { value: 10, name: '安全漏洞' },
            { value: 25, name: 'UI问题' },
            { value: 20, name: '其他' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      defectChart.setOption(defectOption)

      // 响应式调整
      window.addEventListener('resize', () => {
        defectChart.resize()
      })
    }
  }, [])

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>测试概览仪表盘</h1>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic title="总测试用例" value={1280} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="通过率" value={97} suffix="%" />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="覆盖率" value={88} suffix="%" />
          </Card>
        </Col>
      </Row>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <div ref={passRateRef} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <div ref={coverageRef} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <div ref={defectRef} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard