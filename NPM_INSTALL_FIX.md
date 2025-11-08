# NPM安装权限问题解决方案

## 问题描述

安装 `https://api-code.deepvlab.ai/install` 时遇到权限错误：
```
npm error code EACCES
npm error syscall rename
npm error errno -13
```

**根本原因**: `~/.npm` 和 `~/.npm-global` 目录被root用户拥有，需要修复权限。

---

## 解决方案

### 方案 1: 修复权限后安装（推荐）

**步骤 1.1**: 修复npm缓存目录权限
```bash
sudo chown -R $USER:$GROUP ~/.npm
```

**步骤 1.2**: 修复npm全局目录权限
```bash
sudo chown -R $USER:$GROUP ~/.npm-global
```

**步骤 1.3**: 更新PATH环境变量（如果还没更新）
```bash
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
```

**步骤 1.4**: 安装npm包
```bash
npm install -g https://api-code.deepvlab.ai/install
```

---

### 方案 2: 使用npx（无需安装）

如果不想全局安装，可以直接使用npx运行：

```bash
npx --yes https://api-code.deepvlab.ai/install
```

**注意**: 这个包似乎需要登录认证，可能会提示输入凭证。

---

### 方案 3: 本地安装（无需sudo）

**步骤 3.1**: 创建项目目录
```bash
mkdir -p ~/deepv-project
cd ~/deepv-project
```

**步骤 3.2**: 初始化npm项目
```bash
npm init -y
```

**步骤 3.3**: 本地安装包
```bash
npm install https://api-code.deepvlab.ai/install
```

**步骤 3.4**: 运行（查看package.json中的bin字段）
```bash
npx deepv-code  # 或查找正确的命令
```

---

### 方案 4: 使用Docker（隔离环境）

**步骤 4.1**: 创建Dockerfile
```dockerfile
FROM node:20-slim
RUN npm install -g https://api-code.deepvlab.ai/install
ENTRYPOINT ["deepv-code"]
```

**步骤 4.2**: 构建镜像
```bash
docker build -t deepv-code-tool .
```

**步骤 4.3**: 运行容器
```bash
docker run -it deepv-code-tool
```

---

## 快速修复脚本

复制以下命令并粘贴到终端执行：

```bash
# 修复权限
sudo chown -R $USER:$GROUP ~/.npm ~/.npm-global 2>/dev/null

# 更新PATH（如果之前没更新）
if ! grep -q ".npm-global/bin" ~/.bash_profile; then
    echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bash_profile
    echo "已更新~/.bash_profile，请运行: source ~/.bash_profile"
fi

# 安装
npm install -g https://api-code.deepvlab.ai/install
```

---

## 验证安装

安装完成后，验证是否成功：

```bash
# 检查是否安装成功
which deepv-code  # 或查找正确的命令名

# 查看版本/help
deepv-code --version  # 或 deepv-code --help
```

---

## 故障排除

### 问题 1: 仍然遇到权限错误

**解决**:
```bash
# 检查目录所有权
ls -la ~/.npm | head -5
ls -la ~/.npm-global | head -5

# 如果仍然显示root，手动修复
sudo chown -R $(id -u):$(id -g) ~/.npm ~/.npm-global
```

### 问题 2: 命令未找到

**解决**:
```bash
# 确认PATH已更新
source ~/.bash_profile
# 或
export PATH="$HOME/.npm-global/bin:$PATH"

# 重新检查
deepv-code --help
```

### 问题 3: 网络问题

**解决**:
```bash
# 使用代理（如果需要）
npm config set proxy http://proxy.company.com:8080
npm config set https-proxy http://proxy.company.com:8080

# 然后重试安装
npm install -g https://api-code.deepvlab.ai/install
```

---

## NPM配置说明

已经完成的配置：
```
当前npm全局路径: ~/.npm-global/
当前npm缓存路径: ~/.npm/
```

需要手动执行的：
1. 修复权限（需要sudo）
2. 更新PATH环境变量
3. 重新尝试安装

---

## 额外资源

- NPM文档: https://docs.npmjs.com/
- 智谱AI文档: https://open.bigmodel.cn/dev/api
- Node.js权限问题: https://docs.npmjs.com/resolving-eacces-permissions-errors

