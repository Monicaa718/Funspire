# Funspire Agent

全球文化适配的内容引擎 / 内容辅助智能体

## 项目简介

Funspire Agent 是面向中文短剧出海场景的文化适配诊断工具。当前 MVP 聚焦北美市场，基于专家修改意见构建规则库，用户输入中文短剧片段后，系统自动识别文化适配问题、商业钩子缺失、合规风险和世界观真实感问题，输出四维评分、命中规则详情、修改建议和可下载的 Markdown 诊断报告。

## 核心功能

| 功能 | 说明 |
|---|---|
| 关键词规则匹配 | 将剧本文本与北美专家规则库（99 条）的触发关键词进行匹配 |
| 四维评分 | 文化适配分、商业钩子分、合规安全分、世界观真实感分（各 0-100） |
| 非线性文化扣分 | 命中规则数量越多，单条边际扣分越低，避免长剧本分数无意义归零 |
| 钩子关键词加分 | 检测强钩子词（如"背叛""复仇""继承"等），每词 +6 分，上限 100 |
| 命中规则详情 | 展示每条命中规则的问题、原因、修改建议、严重程度、专家来源 |
| 改写方向生成 | 汇总命中规则，输出结构化的中文优化方向（可选英文适配方向） |
| Markdown 报告导出 | 一键下载完整诊断报告 |

## 技术栈

- **前端**：Streamlit 1.40.1
- **语言**：Python 3
- **数据**：JSON 格式专家规则库（无数据库依赖）
- **部署**：Streamlit Community Cloud / Docker

## 数据结构

```
data/
├── rules_expert_na.json      # 北美专家规则库（99 条，Demo 主数据源）
├── expert_cases.json          # 结构化专家标注数据（含元信息）
├── project_scripts.json       # 4 个项目的完整剧本文本（供后续 RAG 使用）
└── menu_config.json           # UI 菜单结构与市场/语言配置
```

### 规则字段说明（`rules_expert_na.json`）

每条规则包含 14 个字段：

| 字段 | 说明 | 示例 |
|---|---|---|
| `rule_id` | 规则唯一标识 | `NA_DIVORCED_002` |
| `case_id` | 项目内案例标识 | `case_002` |
| `project_title` | 来源项目名称 | `The Divorced Hale Heiress` |
| `category` | 问题分类 | `女主独立` / `商业逻辑` / `黄金三秒` / `合规风险` / `世界观适配` |
| `market` | 目标市场 | `北美` |
| `genre` | 题材分类 | `CEO 霸总・豪门逆袭` |
| `trigger_keywords` | 触发关键词列表 | `["下跪", "下跪认错"]` |
| `problem` | 问题描述 | 短文本 |
| `reason` | 在目标市场中产生问题的原因 | 短文本 |
| `suggestion` | 修改建议 | 短文本 |
| `example_before` | 原始问题文本 | 短文本 |
| `example_after` | 建议修改后文本 | 短文本 |
| `severity` | 严重程度 | `high` / `medium` / `low` |
| `source` | 专家来源标注 | `刘觐恺专家标注｜The Divorced Hale Heiress｜case_002` |

### 当前数据覆盖

| 市场 | 规则数 | 覆盖项目 |
|---|---|---|
| 北美 | 99 | 4 个（CEO霸总豪门逆袭、先婚后爱替嫁契约、狼人宿命伴侣、黑手党双强博弈） |
| 其他市场 | 0（资源位预留） | — |

## 本地运行

```bash
# 克隆仓库
git clone <repo-url>
cd AI_agent

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app.py
```

启动后浏览器访问 `http://localhost:8501`。

## 部署方式

### Streamlit Community Cloud

1. 将代码推送到 GitHub
2. 前往 [share.streamlit.io](https://share.streamlit.io)
3. 关联仓库，指定 `app.py` 为入口，点击部署

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t funspire-agent .
docker run -p 8501:8501 funspire-agent
```

## 当前限制

- **仅支持北美市场**：规则匹配仅对北美市场生效，选择其他市场会显示资源位预留提示
- **仅关键词匹配**：使用精确子串匹配（`kw in script`），不支持正则或语义匹配
- **未接入大模型**：诊断和建议完全来自规则库匹配，无 AI 生成改写
- **评分参数硬编码**：钩子分基准值 48、真实感分基准值 76 为硬编码；合规分和真实感分使用无上限线性扣分
- **规则库无版本管理**：99 条规则存储在单一 JSON 文件中，无版本号、审核状态等字段
- **题材字段格式不统一**：`genre` 存在 `"CEO 霸总・豪门逆袭"` 与 `"CEO霸总·豪门逆袭"` 两种写法，可能导致匹配遗漏
- **无用户系统**：无账户体系，不支持项目持久化存储

## 后续规划

| 阶段 | 范围 | 状态 |
|---|---|---|
| MVP | 北美专家规则匹配 + Streamlit Demo | 当前 |
| 第二阶段 | 多市场规则库（拉美、东南亚、中东、日韩、欧洲） | 规划中 |
| 第三阶段 | 接入大模型，实现语义匹配与改写生成 | 规划中 |
| 第四阶段 | 平台合规检测（TikTok、YouTube、ReelShort） | 规划中 |
| 第五阶段 | 多地区版本生成、台词本土化润色 | 规划中 |
