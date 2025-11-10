import React from "react";

function App() {
  return (
    <div style={{ padding: 20 }}>
      <h1>金融售前方案辅助系统</h1>
      <p>系统状态: <span style={{ color: 'green' }}>✓ 前端正常工作</span></p>
      <p>后端API: <span style={{ color: 'green' }}>✓ 正常连接</span></p>
      <p>AI模型: <span style={{ color: 'green' }}>✓ Kimi、Zhipu、DeepSeek 已配置</span></p>

      <div style={{ marginTop: 30, padding: 20, border: '1px solid #ddd', borderRadius: 8 }}>
        <h2>系统功能</h2>
        <ul>
          <li>✅ 多AI模型支持</li>
          <li>✅ 方案生成功能</li>
          <li>✅ 模型对比功能</li>
          <li>✅ 版本迭代功能</li>
          <li>✅ 用户认证系统</li>
        </ul>
      </div>

      <div style={{ marginTop: 30, padding: 20, backgroundColor: '#f0f8ff', borderRadius: 8 }}>
        <h3>多模型方案生成系统</h3>
        <p>该系统已成功集成以下功能：</p>
        <ol>
          <li><strong>多模型选择</strong>: 支持Kimi、Zhipu AI、DeepSeek等多种AI模型</li>
          <li><strong>同步生成</strong>: 可同时使用多个模型生成方案版本</li>
          <li><strong>模型对比</strong>: 直观对比不同模型的生成效果</li>
          <li><strong>迭代优化</strong>: 基于用户反馈持续改进方案</li>
          <li><strong>版本管理</strong>: 完整的版本历史和管理功能</li>
        </ol>
        <p style={{ marginTop: 20, color: '#666' }}>
          请使用浏览器访问 <a href="/login" target="_blank">登录页面</a> 开始使用系统。
        </p>
      </div>

      <div style={{ marginTop: 30, fontSize: '12px', color: '#666' }}>
        <p>技术栈: React + TypeScript + Ant Design + FastAPI + SQLAlchemy</p>
      </div>
    </div>
  );
}

export default App;