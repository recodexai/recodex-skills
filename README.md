# RecodeX Intelligence Skill

<p align="center">
  <strong>🚀 AI Agent 原生的全球创投情报源</strong><br>
  <em>不是 RSS，不是 API —— 是 Agent 可以直接理解、检索和行动的结构化数据层。</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Reports-507+-6382ff?style=flat-square" alt="Reports">
  <img src="https://img.shields.io/badge/Categories-17-a855f7?style=flat-square" alt="Categories">
  <img src="https://img.shields.io/badge/Flash_News-7×24-22d3ee?style=flat-square" alt="Flash News">
  <img src="https://img.shields.io/badge/Dependencies-Zero-34d399?style=flat-square" alt="Zero Dependencies">
</p>

---

## What is RecodeX Skill?

RecodeX Intelligence Skill 让 AI Agent（如 Google Gemini / Antigravity）实时检索 [recodex.ai](https://recodex.ai) 的创投情报数据：

- **原创报道**：覆盖 17 个赛道的创业公司融资深度分析
- **结构化元数据**：公司名、融资金额、轮次、投资方、官网
- **7×24 快讯**：实时金融科技资讯
- **自然语言触发**：Agent 自动识别意图并调用

## Quick Start

### Installation

```bash
git clone https://github.com/recodexai/recodex-skills.git ~/.gemini/config/plugins/recodex
```

重启 Agent 会话，Skill 自动加载。

### Usage

直接用自然语言提问：

> "帮我看看今天有哪些 AI 赛道的新融资"
>
> "查一下 a16z 最近投了哪些公司"
>
> "Ocean 这家公司融了多少钱？投资方是谁？"

Agent 会自动调用对应命令返回结构化结果。

## Commands

| Command | Description | Example |
|---------|------------|---------|
| `latest` | 获取最新内容 | `--type startup --limit 10` |
| `search` | 关键词搜索 | `--query "a16z" --type startup` |
| `category` | 按赛道浏览 | `--name "AI人工智能" --limit 10` |
| `company` | 查询特定公司 | `--name "Ocean"` |
| `trending` | 时间范围内容 | `--period today` |
| `funding` | 融资筛选 | `--round "Seed" --limit 20` |

## Output Format

```json
{
  "source": "recodex.ai",
  "count": 1,
  "results": [{
    "id": 240978,
    "title": "Ocean 获 2800 万美元融资...",
    "company_name": "Ocean",
    "funding_round": "Seed",
    "funding_amount": "$2800万",
    "investors": "Lightspeed Venture Partners (领投)...",
    "website": "https://www.ocean.security",
    "excerpt": "..."
  }]
}
```

## Coverage

AI人工智能 (176) · 前沿科技 (55) · 金融科技 (51) · 医疗健康 (48) · 企业SaaS (39) · 生物科技 (37) · 消费品牌 (18) · 气候科技 (18) · 硬件/芯片 (16) · Web3 (10) · 加密货币 (8) · 网络安全 (8) · 娱乐游戏 (5) · 机器人 (5) · 太空科技 (4) · 食品科技 (4) · 风险投资 (3)

## Why Skill > RSS > API?

|  | RSS | REST API | **RecodeX Skill** |
|--|-----|---------|-------------------|
| Agent 可直接理解 | ❌ 需解析 XML | ❌ 需编写代码 | ✅ 结构化 JSON |
| 融资元数据 | ❌ | ⚠️ 需自定义 | ✅ 内置 |
| 按赛道筛选 | ❌ | ⚠️ 需知道 API | ✅ 一条命令 |
| 安装成本 | 中等 | 高 | ✅ git clone 即用 |
| 自然语言触发 | ❌ | ❌ | ✅ Agent 自动识别 |

## Tech Stack

- **Zero dependencies** — 纯 Python stdlib（`urllib`, `json`, `argparse`）
- **Rate limiting** — 1 req/sec，带指数退避重试
- **HTML → Text** — 自动剥离 HTML 标签
- **File output** — 所有结果写入 JSON 文件

## Documentation

📖 [在线文档](https://recodexai.github.io/recodex-skills/)

## License

MIT

---

<p align="center">
  Built by <a href="https://recodex.ai">RecodeX</a> · AI-native intelligence for venture capital
</p>
