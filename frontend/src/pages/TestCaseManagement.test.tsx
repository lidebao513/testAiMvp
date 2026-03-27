import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TestCaseManagement from './TestCaseManagement';

// 模拟antd的message
const mockMessage = {
  success: jest.fn()
};

jest.mock('antd', () => ({
  ...jest.requireActual('antd'),
  message: mockMessage
}));

describe('TestCaseManagement component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders without crashing', () => {
    render(<TestCaseManagement />);
    expect(screen.getByText('AI生成测试用例管理')).toBeInTheDocument();
  });

  test('renders test cases table', () => {
    render(<TestCaseManagement />);
    
    // 验证表格存在
    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('标题')).toBeInTheDocument();
    expect(screen.getByText('类型')).toBeInTheDocument();
    expect(screen.getByText('状态')).toBeInTheDocument();
    expect(screen.getByText('质量')).toBeInTheDocument();
    expect(screen.getByText('生成时间')).toBeInTheDocument();
    expect(screen.getByText('操作')).toBeInTheDocument();
  });

  test('displays initial test cases', () => {
    render(<TestCaseManagement />);
    
    // 验证初始测试用例显示
    expect(screen.getByText('用户登录测试')).toBeInTheDocument();
    expect(screen.getByText('添加商品到购物车')).toBeInTheDocument();
    expect(screen.getByText('计算函数测试')).toBeInTheDocument();
  });

  test('opens preview modal when preview button is clicked', () => {
    render(<TestCaseManagement />);
    
    // 点击预览按钮
    const previewButtons = screen.getAllByText('预览');
    fireEvent.click(previewButtons[0]);
    
    // 验证模态框打开
    expect(screen.getByText('用户登录测试')).toBeInTheDocument();
    expect(screen.getByText('类型:')).toBeInTheDocument();
    expect(screen.getByText('状态:')).toBeInTheDocument();
    expect(screen.getByText('质量:')).toBeInTheDocument();
    expect(screen.getByText('生成时间:')).toBeInTheDocument();
    expect(screen.getByText('内容:')).toBeInTheDocument();
  });

  test('closes preview modal when close button is clicked', () => {
    render(<TestCaseManagement />);
    
    // 点击预览按钮
    const previewButtons = screen.getAllByText('预览');
    fireEvent.click(previewButtons[0]);
    
    // 点击关闭按钮
    const closeButton = screen.getByText('关闭');
    fireEvent.click(closeButton);
    
    // 验证模态框关闭
    expect(screen.queryByText('类型:')).not.toBeInTheDocument();
  });

  test('opens edit modal when edit button is clicked', () => {
    render(<TestCaseManagement />);
    
    // 点击编辑按钮
    const editButtons = screen.getAllByText('编辑');
    fireEvent.click(editButtons[0]);
    
    // 验证编辑模态框打开
    expect(screen.getByText('编辑测试用例: 用户登录测试')).toBeInTheDocument();
  });

  test('saves edited test case content', async () => {
    render(<TestCaseManagement />);
    
    // 点击编辑按钮
    const editButtons = screen.getAllByText('编辑');
    fireEvent.click(editButtons[0]);
    
    // 修改内容
    const textArea = screen.getByRole('textbox');
    fireEvent.change(textArea, { target: { value: 'Modified test content' } });
    
    // 点击保存按钮
    const saveButton = screen.getByText('保存');
    fireEvent.click(saveButton);
    
    // 验证消息提示
    await waitFor(() => {
      expect(mockMessage.success).toHaveBeenCalledWith('测试用例已更新');
    });
  });

  test('updates test case quality when rate is changed', async () => {
    render(<TestCaseManagement />);
    
    // 找到评分组件并点击
    const rateComponents = screen.getAllByRole('slider');
    fireEvent.click(rateComponents[0]);
    
    // 验证消息提示
    await waitFor(() => {
      expect(mockMessage.success).toHaveBeenCalledWith('质量评分已更新');
    });
  });
});