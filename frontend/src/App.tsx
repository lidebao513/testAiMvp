import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Layout, Menu, theme } from 'antd'
import Dashboard from './pages/Dashboard'
import TestCaseManagement from './pages/TestCaseManagement'
import ExecutionMonitoring from './pages/ExecutionMonitoring'
import KnowledgeBase from './pages/KnowledgeBase'

const { Header, Content, Sider } = Layout

function App() {
  const { token: { colorBgContainer } } = theme.useToken()

  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ display: 'flex', alignItems: 'center' }}>
          <div className="logo" style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
            AI测试工程师管理平台
          </div>
        </Header>
        <Layout>
          <Sider width={200} style={{ background: colorBgContainer }}>
            <Menu
              mode="inline"
              defaultSelectedKeys={['dashboard']}
              style={{ height: '100%', borderRight: 0 }}
            >
              <Menu.Item key="dashboard">
                <Link to="/">测试概览</Link>
              </Menu.Item>
              <Menu.Item key="test-cases">
                <Link to="/test-cases">测试用例管理</Link>
              </Menu.Item>
              <Menu.Item key="execution">
                <Link to="/execution">执行监控</Link>
              </Menu.Item>
              <Menu.Item key="knowledge">
                <Link to="/knowledge">知识库管理</Link>
              </Menu.Item>
            </Menu>
          </Sider>
          <Layout style={{ padding: '0 24px 24px' }}>
            <Content
              style={{
                padding: 24,
                margin: 0,
                minHeight: 280,
                background: colorBgContainer,
              }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/test-cases" element={<TestCaseManagement />} />
                <Route path="/execution" element={<ExecutionMonitoring />} />
                <Route path="/knowledge" element={<KnowledgeBase />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Layout>
    </Router>
  )
}

export default App