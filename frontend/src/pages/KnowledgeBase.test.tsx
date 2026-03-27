import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import KnowledgeBase from './KnowledgeBase';

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

// 模拟console.log
const mockConsoleLog = jest.spyOn(console, 'log').mockImplementation();

describe('KnowledgeBase component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders without crashing', () => {
    render(<KnowledgeBase />);
    expect(screen.getByText('知识库管理')).toBeInTheDocument();
  });

  test('renders test pattern visualization', () => {
    render(<KnowledgeBase />);
    expect(screen.getByText('测试模式可视化')).toBeInTheDocument();
    expect(mockInit).toHaveBeenCalledTimes(1);
  });

  test('renders defect search functionality', () => {
    render(<KnowledgeBase />);
    expect(screen.getByText('历史缺陷检索')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('输入缺陷关键词')).toBeInTheDocument();
  });

  test('handles search functionality', () => {
    render(<KnowledgeBase />);
    
    // 输入搜索关键词
    const searchInput = screen.getByPlaceholderText('输入缺陷关键词');
    fireEvent.change(searchInput, { target: { value: '登录' } });
    
    // 点击搜索按钮
    const searchButton = screen.getByText('搜索');
    fireEvent.click(searchButton);
    
    // 验证搜索函数被调用
    expect(mockConsoleLog).toHaveBeenCalledWith('搜索:', '登录');
  });

  test('renders defect table', () => {
    render(<KnowledgeBase />);
    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('标题')).toBeInTheDocument();
    expect(screen.getByText('严重程度')).toBeInTheDocument();
    expect(screen.getByText('状态')).toBeInTheDocument();
    expect(screen.getByText('创建时间')).toBeInTheDocument();
    expect(screen.getByText('操作')).toBeInTheDocument();
  });

  test('renders similar test cases table', () => {
    render(<KnowledgeBase />);
    expect(screen.getByText('相似用例推荐')).toBeInTheDocument();
    expect(screen.getByText('用户登录测试')).toBeInTheDocument();
    expect(screen.getByText('管理员登录测试')).toBeInTheDocument();
    expect(screen.getByText('登录失败测试')).toBeInTheDocument();
  });

  test('opens defect modal when view button is clicked', () => {
    render(<KnowledgeBase />);
    
    // 点击查看按钮
    const viewButtons = screen.getAllByText('查看');
    fireEvent.click(viewButtons[0]);
    
    // 验证模态框打开
    expect(screen.getByText('登录页面响应慢')).toBeInTheDocument();
  });

  test('closes defect modal when close button is clicked', () => {
    render(<KnowledgeBase />);
    
    // 点击查看按钮
    const viewButtons = screen.getAllByText('查看');
    fireEvent.click(viewButtons[0]);
    
    // 点击关闭按钮
    const closeButton = screen.getByText('关闭');
    fireEvent.click(closeButton);
    
    // 验证模态框关闭
    expect(screen.queryByText('严重程度:')).not.toBeInTheDocument();
  });

  test('displays defect details in modal', () => {
    render(<KnowledgeBase />);
    
    // 点击查看按钮
    const viewButtons = screen.getAllByText('查看');
    fireEvent.click(viewButtons[0]);
    
    // 验证缺陷详情显示
    expect(screen.getByText('严重程度:')).toBeInTheDocument();
    expect(screen.getByText('状态:')).toBeInTheDocument();
    expect(screen.getByText('创建时间:')).toBeInTheDocument();
    expect(screen.getByText('描述:')).toBeInTheDocument();
  });
});