import { render, screen, act } from '@testing-library/react';
import Dashboard from './Dashboard';

// 模拟echarts库
const mockInit = jest.fn(() => ({
  setOption: jest.fn(),
  resize: jest.fn(),
  dispose: jest.fn()
}));

const mockEcharts = {
  init: mockInit,
  graphic: {
    LinearGradient: jest.fn(() => ({}))
  }
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

describe('Dashboard component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders without crashing', () => {
    render(<Dashboard />);
    expect(screen.getByText('测试概览仪表盘')).toBeInTheDocument();
  });

  test('renders statistics cards', () => {
    render(<Dashboard />);
    expect(screen.getByText('总测试用例')).toBeInTheDocument();
    expect(screen.getByText('通过率')).toBeInTheDocument();
    expect(screen.getByText('覆盖率')).toBeInTheDocument();
  });

  test('initializes charts on mount', () => {
    render(<Dashboard />);
    
    // 验证echarts.init被调用了3次（三个图表）
    expect(mockInit).toHaveBeenCalledTimes(3);
    
    // 验证window.resize事件监听器被添加了3次（每个图表一个）
    expect(mockAddEventListener).toHaveBeenCalledTimes(3);
    expect(mockAddEventListener).toHaveBeenCalledWith('resize', expect.any(Function));
  });

  test('renders chart containers', () => {
    render(<Dashboard />);
    
    // 验证图表容器存在
    const chartContainers = document.querySelectorAll('[style*="height: 300"]');
    expect(chartContainers.length).toBe(3);
  });

  test('displays correct statistic values', () => {
    render(<Dashboard />);
    
    // 验证统计数据显示
    expect(screen.getByText('1280')).toBeInTheDocument();
    expect(screen.getByText('97%')).toBeInTheDocument();
    expect(screen.getByText('88%')).toBeInTheDocument();
  });

  test('cleans up event listeners and disposes charts on unmount', () => {
    const { unmount } = render(<Dashboard />);
    
    // 获取模拟的chart实例
    const chartInstances = mockInit.mock.results.map(result => result.value);
    
    // 卸载组件
    unmount();
    
    // 验证window.resize事件监听器被移除了3次（每个图表一个）
    expect(mockRemoveEventListener).toHaveBeenCalledTimes(3);
    
    // 验证每个chart实例的dispose方法都被调用了
    chartInstances.forEach(instance => {
      expect(instance.dispose).toHaveBeenCalled();
    });
  });

  test('calls chart resize method on window resize', () => {
    render(<Dashboard />);
    
    // 获取模拟的chart实例
    const chartInstances = mockInit.mock.results.map(result => result.value);
    
    // 模拟window.resize事件
    act(() => {
      const resizeEvent = new Event('resize');
      window.dispatchEvent(resizeEvent);
    });
    
    // 验证每个chart实例的resize方法都被调用了
    chartInstances.forEach(instance => {
      expect(instance.resize).toHaveBeenCalled();
    });
  });
});