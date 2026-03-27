import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ExecutionMonitoring from './ExecutionMonitoring';

// 模拟echarts库
const mockInit = jest.fn(() => ({
  setOption: jest.fn(),
  resize: jest.fn(),
  destroy: jest.fn()
}));

const mockEcharts = {
  init: mockInit
};

jest.mock('echarts', () => mockEcharts);

// 模拟window.resize事件
const mockAddEventListener = jest.fn();
const mockRemoveEventListener = jest.fn();

Object.defineProperty(window, 'addEventListener', {
  value: mockAddEventListener
});

Object.defineProperty(window, 'removeEventListener', {
  value: mockRemoveEventListener
});

describe('ExecutionMonitoring component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders without crashing', () => {
    render(<ExecutionMonitoring />);
    expect(screen.getByText('智能执行监控')).toBeInTheDocument();
  });

  test('renders statistics cards', () => {
    render(<ExecutionMonitoring />);
    expect(screen.getByText('成功用例')).toBeInTheDocument();
    expect(screen.getByText('失败用例')).toBeInTheDocument();
    expect(screen.getByText('总执行时长')).toBeInTheDocument();
  });

  test('displays correct statistics values', () => {
    render(<ExecutionMonitoring />);
    
    // 验证统计数据显示
    expect(screen.getByText('3')).toBeInTheDocument(); // 成功用例
    expect(screen.getByText('2')).toBeInTheDocument(); // 失败用例
    expect(screen.getByText('14.10秒')).toBeInTheDocument(); // 总执行时长
  });

  test('renders execution logs timeline', () => {
    render(<ExecutionMonitoring />);
    expect(screen.getByText('实时执行日志')).toBeInTheDocument();
    expect(screen.getByText('用户登录测试')).toBeInTheDocument();
    expect(screen.getByText('商品列表测试')).toBeInTheDocument();
    expect(screen.getByText('购物车测试')).toBeInTheDocument();
    expect(screen.getByText('支付测试')).toBeInTheDocument();
    expect(screen.getByText('订单测试')).toBeInTheDocument();
  });

  test('renders execution duration chart', () => {
    render(<ExecutionMonitoring />);
    expect(screen.getByText('执行时长分布')).toBeInTheDocument();
    expect(mockInit).toHaveBeenCalledTimes(1);
  });

  test('renders execution details table', () => {
    render(<ExecutionMonitoring />);
    expect(screen.getByText('执行详情')).toBeInTheDocument();
    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('测试名称')).toBeInTheDocument();
    expect(screen.getByText('状态')).toBeInTheDocument();
    expect(screen.getByText('执行时长 (秒)')).toBeInTheDocument();
    expect(screen.getByText('执行时间')).toBeInTheDocument();
    expect(screen.getByText('操作')).toBeInTheDocument();
  });

  test('opens screenshot modal when view screenshot button is clicked', () => {
    render(<ExecutionMonitoring />);
    
    // 点击查看截图按钮
    const viewScreenshotButtons = screen.getAllByText('查看截图');
    fireEvent.click(viewScreenshotButtons[0]);
    
    // 验证模态框打开
    expect(screen.getByText('商品列表测试 - 失败截图')).toBeInTheDocument();
  });

  test('closes screenshot modal when close button is clicked', () => {
    render(<ExecutionMonitoring />);
    
    // 点击查看截图按钮
    const viewScreenshotButtons = screen.getAllByText('查看截图');
    fireEvent.click(viewScreenshotButtons[0]);
    
    // 点击关闭按钮
    const closeButton = screen.getByText('关闭');
    fireEvent.click(closeButton);
    
    // 验证模态框关闭
    expect(screen.queryByText('商品列表测试 - 失败截图')).not.toBeInTheDocument();
  });

  test('displays error message in screenshot modal', () => {
    render(<ExecutionMonitoring />);
    
    // 点击查看截图按钮
    const viewScreenshotButtons = screen.getAllByText('查看截图');
    fireEvent.click(viewScreenshotButtons[0]);
    
    // 验证错误信息显示
    expect(screen.getByText('错误信息:')).toBeInTheDocument();
    expect(screen.getByText('AssertionError: Expected 200, got 404')).toBeInTheDocument();
  });
});