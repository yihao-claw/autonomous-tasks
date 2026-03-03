# DDG Search Skill for OpenClaw

🔍 **无需 API 密钥的网络搜索工具**

## 📦 已安装

位置: `/home/node/.openclaw/workspace/skills/ddg-search`

## ⚡ 快速使用

### 方法 1: 命令行
```bash
python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "你的搜索词"
```

### 方法 2: 包装脚本
```bash
bash /home/node/.openclaw/workspace/ddg-search-tool.sh "你的搜索词"
```

### 方法 3: OpenClaw Agent
```bash
# 在 agent 中使用（需要 skill 被加载）
/ddg-search "Claude AI"
```

## 📊 参数

```bash
python3 ddg_search.py [选项] 搜索词

选项:
  -n, --num-results    搜索结果数量（默认: 10）
  --json               输出 JSON 格式
  -h, --help           显示帮助信息
```

## 💡 示例

```bash
# 搜索 OpenClaw
python3 ddg_search.py "OpenClaw"

# 搜索并只返回 5 个结果
python3 ddg_search.py "Python tutorial" -n 5

# 获取 JSON 格式的输出
python3 ddg_search.py "Claude AI" --json

# 格式化 JSON 输出
python3 ddg_search.py "test" --json | python3 -m json.tool
```

## ✅ 特点

- ✅ 无需 API 密钥
- ✅ 使用 DuckDuckGo 搜索
- ✅ 隐私友好
- ✅ JSON 格式输出
- ✅ 可定制结果数量
- ✅ 开箱即用

## 📁 文件结构

```
ddg-search/
├── ddg_search.py              # 主搜索脚本
├── index.js                   # Node.js 接口
├── package.json               # 依赖配置
├── openclaw.plugin.json       # OpenClaw 配置
├── SKILL.md                   # Skill 描述
└── README.md                  # 本文件
```

## 🔗 相关资源

- 快速开始: `~/.openclaw/QUICK_START_DDG.md`
- 详细文档: `~/.openclaw/workspace/DDG_SEARCH_USAGE.md`
- 完整设置: `~/.openclaw/workspace/SETUP_COMPLETE.md`

---

**现在你可以搜索任何内容，无需 API 密钥！** 🚀
