#!/bin/bash

echo "🔧 修复前端代码格式问题..."

# 安装React类型定义
cd /Users/zhangyanlong/workspaces/Fin_Pre_Assist/frontend
npm install --save-dev @types/react @types/react-dom

# 修复import React问题
find src -name "*.tsx" -o -name "*.ts" | xargs sed -i '' '1i\
import React from "react";
'

# 移除未使用的变量
sed -i '' 's/, success, data/, successData/g' src/components/ProposalGenerationProgress.tsx

# 添加ESLint环境变量
cat >> .eslintrc.json << 'EOF'

  "globals": {
    "React": "readonly",
    "describe": "readonly",
    "it": "readonly", 
    "expect": "readonly",
    "__dirname": "readonly"
  }
EOF

echo "✅ 前端代码格式修复完成"