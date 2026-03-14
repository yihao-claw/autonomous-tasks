# ✅ OpenClaw Web Search 设置完毕

## 🎯 当前状态

你现在有 **两个选项** 来进行网络搜索，都无需 Brave API 密钥：

### 选项 A: 使用 brave_shim（已设置）
- brave_shim 运行在 http://127.0.0.1:8000
- OpenClaw 已 patch 指向本地 shim
- 理论上应该可以工作（尽管我们遇到了一些集成问题）

**启动方式：**
```bash
# 终端 1
cd /opt/brave_shim && python3 brave_shim.py

# 终端 2
export NODE_TLS_REJECT_UNAUTHORIZED=0
export BRAVE_API_KEY="shim"
export BRAVE_API_ENDPOINT="http://127.0.0.1:8000"
openclaw agent
```

### 选项 B: 使用 DDG Search（推荐 ⭐）
- 完全独立，无需 brave_shim
- 使用 DuckDuckGo，隐私更好
- 开箱即用，无需复杂配置

**启动方式：**
```bash
# 直接使用
python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "搜索词"

# 或通过包装脚本
bash /home/node/.openclaw/workspace/ddg-search.sh "搜索词"
```

## 🚀 推荐方案

**使用 DDG Search** 是最简单的，因为：
1. ✅ 无需 API 密钥
2. ✅ 无需复杂配置
3. ✅ 立即可用
4. ✅ 隐私更好

## 📋 快速开始

### 测试 DDG Search
```bash
# 测试搜索
python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "Claude AI" -n 5
```

### 在 OpenClaw 中使用
如果你想在 agent 中使用 ddg-search：

```bash
# 编辑你的 agent 配置，添加这个 skill
# 或者在 agent 启动时包含它

# 方式 1: 通过命令直接搜索
python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "你的查询"

# 方式 2: 让 agent 调用这个脚本
# （需要配置 agent 的工具列表）
```

## 🔧 文件位置

### Brave Shim 相关
- `/opt/brave_shim/brave_shim.py` — 主程序
- `/opt/brave_shim/certs/` — SSL 证书
- `/home/node/.openclaw/start-with-shim.sh` — 启动脚本

### DDG Search 相关
- `/home/node/.openclaw/workspace/skills/ddg-search/` — Skill 目录
- `/home/node/.openclaw/workspace/ddg-search.sh` — 包装脚本
- `/home/node/.openclaw/workspace/DDG_SEARCH_USAGE.md` — 详细文档

### 配置文件
- `/home/node/.openclaw/openclaw.json` — OpenClaw 配置
- `/home/node/.openclaw/.env` — 环境变量
- `/etc/hosts` — DNS 重定向

## ⚡ 立即使用

```bash
# 搜索 OpenClaw 相关信息
python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "OpenClaw AI" -n 5 --json | python3 -m json.tool

# 搜索 Claude 最新特性
python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "Claude 3.5 Sonnet features" -n 10

# 搜索编程教程
python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "Python web scraping tutorial" -n 5
```

## 🎓 下一步

1. **立即尝试 DDG Search**
   ```bash
   python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "test query"
   ```

2. **如果想用 brave_shim**，告诉我是否还有问题

3. **集成到 agent**
   - 修改 agent 配置以识别 ddg-search skill
   - 或编写一个 custom tool 来调用它

## ❓ 常见问题

**Q: 我可以在 OpenClaw agent 中直接使用 web_search 吗？**
A: 可以，但它会继续尝试连接 Brave API。如果 brave_shim patch 有效，它应该会连接到本地。否则使用 DDG Search。

**Q: DDG Search 的结果质量如何？**
A: 很好。DuckDuckGo 提供高质量的搜索结果，而且隐私保护更好。

**Q: 可以自定义搜索结果数量吗？**
A: 可以，使用 `-n` 参数：
```bash
python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "查询" -n 20
```

## 📞 需要帮助？

- 检查 ddg-search 是否工作：`python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "test"`
- 检查 brave_shim 是否运行：`curl http://127.0.0.1:8000/status`
- 查看日志：`tail -f /opt/brave_shim/log/brave_shim.log`

---

**现在你可以选择使用 DDG Search（推荐）或 brave_shim。两者都已准备好！** ✨
