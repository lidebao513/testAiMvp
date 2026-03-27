import React from 'react'

const TestPage: React.FC = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>测试页面</h1>
      <p>这是一个测试页面，用于验证React渲染是否正常。</p>
      <button onClick={() => alert('测试按钮点击成功！')}>点击测试</button>
    </div>
  )
}

export default TestPage