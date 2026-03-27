import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

// 模拟antd的theme
jest.mock('antd', () => ({
  ...jest.requireActual('antd'),
  theme: {
    useToken: () => ({
      token: { colorBgContainer: '#fff' }
    })
  }
}));

describe('App component', () => {
  test('renders without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    expect(screen.getByText('AI测试工程师管理平台')).toBeInTheDocument();
  });

  test('renders navigation menu items', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    expect(screen.getByText('测试概览')).toBeInTheDocument();
    expect(screen.getByText('测试用例管理')).toBeInTheDocument();
    expect(screen.getByText('执行监控')).toBeInTheDocument();
    expect(screen.getByText('知识库管理')).toBeInTheDocument();
  });

  test('renders routes correctly', () => {
    render(
      <BrowserRouter initialEntries={['/']}>
        <App />
      </BrowserRouter>
    );
    expect(screen.getByText('测试概览仪表盘')).toBeInTheDocument();
  });

  test('renders test cases route', () => {
    render(
      <BrowserRouter initialEntries={['/test-cases']}>
        <App />
      </BrowserRouter>
    );
    expect(screen.getByText('测试用例管理')).toBeInTheDocument();
  });

  test('renders execution route', () => {
    render(
      <BrowserRouter initialEntries={['/execution']}>
        <App />
      </BrowserRouter>
    );
    expect(screen.getByText('执行监控')).toBeInTheDocument();
  });

  test('renders knowledge route', () => {
    render(
      <BrowserRouter initialEntries={['/knowledge']}>
        <App />
      </BrowserRouter>
    );
    expect(screen.getByText('知识库管理')).toBeInTheDocument();
  });
});