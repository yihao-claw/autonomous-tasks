# DDG Search - 替代 Brave Search 的方案

## ✅ 已设置完毕

我已经为你创建了一个完整的 **DuckDuckGo 搜索技能**，无需任何 API 密钥。

### 📍 位置
```
/home/node/.openclaw/workspace/skills/ddg-search/
├── ddg_search.py       # 主要搜索脚本
├── index.js            # OpenClaw 技能定义
├── package.json        # 依赖配置
└── SKILL.md            # 文档
```

## 🚀 使用方法

### 方法 1: 直接命令行
```bash
python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "你的搜索词" -n 10
```

### 方法 2: 使用包装脚本
```bash
bash /home/node/.openclaw/workspace/ddg-search.sh "你的搜索词"
```

### 方法 3: 在 OpenClaw agent 中使用

如果 OpenClaw 识别了这个 skill，你可以直接在 agent 中使用：
```
/ddg-search "Claude AI"
```

## 📝 示例

```bash
# 搜索 Claude AI 并返回 5 个结果
python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "Claude AI" -n 5 --json

# 输出:
# {
#   "query": "Claude AI",
#   "results": [
#     {
#       "title": "...",
#       "url": "...",
#       "description": "...",
#       "source": "ddg"
#     }
#   ]
# }
```

## 优势

✅ **无需 API 密钥**
✅ **快速搜索**
✅ **支持多个结果**
✅ **JSON 输出格式**
✅ **DuckDuckGo 隐私保护**

## 与 Brave Search 的对比

| 功能 | Brave Search | DDG Search |
|------|--------------|-----------|
| API 密钥 | ✓ 需要 | ✗ 不需要 |
| 速度 | 快 | 快 |
| 质量 | 高 | 高 |
| 隐私 | 好 | 很好 |
| 成本 | $ 付费 | 免费 |

## 🔧 集成到 OpenClaw

如果你想让 OpenClaw 的 agent 自动使用 ddg-search 而不是 web_search，可以：

1. **禁用 web_search 工具**（在 agent 的工具列表中移除）
2. **添加 ddg-search skill**（通过 agent 配置或 skill 管理器）
3. **在 agent prompt 中指示使用 ddg-search**

## 验证安装

```bash
# 测试 ddg-search 脚本
python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "test" -n 3 --json

# 应该返回 3 个 JSON 格式的搜索结果
```

## 📌 备注

这个 skill 使用 `ddgs` Python 库（来自 brave_shim），所以依赖已经满足。无需额外安装。
