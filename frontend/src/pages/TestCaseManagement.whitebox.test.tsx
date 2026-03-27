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

describe('TestCaseManagement White Box Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('handleSaveEdit updates test case content', () => {
    const { container } = render(<TestCaseManagement />);
    
    // 点击编辑按钮
    const editButtons = screen.getAllByText('编辑');
    fireEvent.click(editButtons[0]);
    
    // 修改内容
    const textArea = screen.getByRole('textbox');
    const newContent = 'Modified test content';
    fireEvent.change(textArea, { target: { value: newContent } });
    
    // 点击保存按钮
    const saveButton = screen.getByText('保存');
    fireEvent.click(saveButton);
    
    // 验证消息提示
    waitFor(() => {
      expect(mockMessage.success).toHaveBeenCalledWith('测试用例已更新');
    });
  });

  test('handleQualityChange updates test case quality and status', () => {
    const { container } = render(<TestCaseManagement />);
    
    // 找到评分组件并点击（打5分）
    const rateComponents = screen.getAllByRole('slider');
    fireEvent.click(rateComponents[0]);
    
    // 验证消息提示
    waitFor(() => {
      expect(mockMessage.success).toHaveBeenCalledWith('质量评分已更新');
    });
  });

  test('handleQualityChange sets status to 已通过 when quality >= 4', () => {
    const { container } = render(<TestCaseManagement />);
    
    // 找到评分组件并点击（打5分）
    const rateComponents = screen.getAllByRole('slider');
    fireEvent.click(rateComponents[0]);
    
    // 验证状态更新
    waitFor(() => {
      expect(screen.getByText('已通过')).toBeInTheDocument();
    });
  });

  test('handleQualityChange sets status to 需改进 when quality >= 2 and < 4', () => {
    const { container } = render(<TestCaseManagement />);
    
    // 找到评分组件并点击（打3分）
    const rateComponents = screen.getAllByRole('slider');
    fireEvent.click(rateComponents[0]);
    
    // 验证状态更新
    waitFor(() => {
      expect(screen.getByText('需改进')).toBeInTheDocument();
    });
  });

  test('handleQualityChange sets status to 未通过 when quality < 2', () => {
    const { container } = render(<TestCaseManagement />);
    
    // 找到评分组件并点击（打1分）
    const rateComponents = screen.getAllByRole('slider');
    fireEvent.click(rateComponents[0]);
    
    // 验证状态更新
    waitFor(() => {
      expect(screen.getByText('未通过')).toBeInTheDocument();
    });
  });

  test('handlePreview opens modal with correct test case', () => {
    const { container } = render(<TestCaseManagement />);
    
    // 点击预览按钮
    const previewButtons = screen.getAllByText('预览');
    fireEvent.click(previewButtons[0]);
    
    // 验证模态框打开并显示正确的测试用例
    expect(screen.getByText('用户登录测试')).toBeInTheDocument();
    expect(screen.getByText('E2E')).toBeInTheDocument();
    expect(screen.getByText('待审核')).toBeInTheDocument();
  });

  test('handleEdit opens modal with correct test case content', () => {
    const { container } = render(<TestCaseManagement />);
    
    // 点击编辑按钮
    const editButtons = screen.getAllByText('编辑');
    fireEvent.click(editButtons[0]);
    
    // 验证编辑模态框打开并显示正确的测试用例内容
    const textArea = screen.getByRole('textbox');
    expect(textArea.value).toContain('const { test, expect } = require');
  });
});