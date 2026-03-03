# Brave Shim 集成 — 最终解决方案

## ✅ 已完成的设置

### 1. brave_shim 已运行
- HTTP 服务: http://127.0.0.1:8000 ✓
- HTTPS 服务: https://127.0.0.1:8443 ✓
- 直接测试: `curl http://127.0.0.1:8000/res/v1/web/search?q=test` ✓

### 2. OpenClaw 代码已 Patch
- 所有 Brave API 调用已改为 `http://127.0.0.1:8000`
- 10 个文件中的引用已修改 ✓
- 文件位置: `/usr/local/lib/node_modules/openclaw/dist/**/*.js` ✓

### 3. 网络配置已完成
- /etc/hosts: `127.0.0.1 api.search.brave.com` ✓
- 环境变量已设置 ✓
- 自签名证书已生成 ✓

## 🔧 使用方法

### 最简单的启动方式
```bash
# 确保 brave_shim 运行中
cd /opt/brave_shim && python3 brave_shim.py &

# 启动 OpenClaw（使用准备好的脚本）
bash /home/node/.openclaw/start-with-shim.sh
```

### 或直接启动 OpenClaw
```bash
export NODE_TLS_REJECT_UNAUTHORIZED=0
export BRAVE_API_KEY="shim"
export BRAVE_API_ENDPOINT="http://127.0.0.1:8000"

openclaw agent
```

## 🎯 验证配置

### 检查 brave_shim
```bash
curl http://127.0.0.1:8000/status
```

### 检查 OpenClaw 代码补丁
```bash
grep -c "http://127.0.0.1:8000" /usr/local/lib/node_modules/openclaw/dist/**/*.js
```

### 检查 /etc/hosts
```bash
grep "api.search.brave.com" /etc/hosts
```

## 📋 文件列表

已修改/创建的文件：
- `/etc/hosts` — DNS 重定向
- `/home/node/.openclaw/openclaw.json` — 工具配置
- `/home/node/.openclaw/.env` — 环境变量
- `/opt/brave_shim/brave_shim.py` — 支持 HTTPS
- `/opt/brave_shim/certs/` — 自签名证书
- `/usr/local/lib/node_modules/openclaw/dist/**/*.js` — Patch 代码
- `/home/node/.openclaw/start-with-shim.sh` — 启动脚本

## ⚠️ 已知问题

**web_search tool 仍可能无法连接到 brave_shim** 的原因可能是：
1. web_search 实现在 Anthropic SDK 内部，不依赖 OpenClaw dist 代码
2. 可能需要完全重启系统或网关
3. 可能需要使用替代方案（ddg-search skill 或其他搜索工具）

## 🔄 备选方案

如果上述方法仍不工作，可以：
1. 使用 `ddg-search` skill (需要 `npx playbooks add skill openclaw/skills --skill ddg-search`)
2. 禁用 web_search，使用 custom 搜索工具
3. 使用 Perplexity API 替代 Brave Search

## 🚀 下一步

让我知道：
- web_search 是否现在能工作？
- 如果仍有问题，你之前怎样配置 brave_shim 让它工作的？
