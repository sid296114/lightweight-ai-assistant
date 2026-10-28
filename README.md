# 轻量AI助手 Web端

面向学生、开发者、办公人群的轻量化在线 AI 工作台。支持流式 AI 对话、Markdown / 代码高亮渲染、文档解析（TXT / Markdown / PDF）、AI 生图工作台与账号体系。

- 产品需求：`PRD.md`（V1.0）
- 技术设计：`TECH_DESIGN.md`（V1.0）
- 工程规则：`AGENTS.md`

## 技术栈

| 层次 | 选型 |
| --- | --- |
| 前端 | Vue3 + Vite + TailwindCSS + Pinia + Vue Router（纯 Tailwind 手写组件，无组件库） |
| 后端 | Python FastAPI + SQLAlchemy 2.0 + PyMySQL |
| 数据库 | MySQL 8.0（`user` / `chat_session` / `chat_message` 三表首期全建） |
| 鉴权 | JWT（7 天）+ bcrypt 密码哈希 + 登录频率限制 |
| AI 能力 | OpenAI 兼容大模型接口（SSE 流式）、PyMuPDF 文档解析、AI 绘图接口（预留） |

## 目录结构

```
project/
├── PRD.md / TECH_DESIGN.md / AGENTS.md    # 设计文档
├── backend/                               # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py                        # 应用入口（启动时自动建表）
│   │   ├── config.py                      # .env 配置读取
│   │   ├── models.py / schemas.py         # ORM 模型 / Pydantic 模型
│   │   ├── security.py / deps.py          # bcrypt + JWT / 依赖注入
│   │   ├── routers/                       # auth / chat / files / draw
│   │   └── services/                      # llm（SSE 转发 + mock）/ file_parser
│   ├── smoke_test.py                      # 后端接口冒烟测试（16 项）
│   ├── providers_test.py                  # 大模型服务商接口测试（13 项）
│   ├── providers.json                     # 服务商配置（含各平台 API Key，仅存后端，勿提交）
│   ├── .env.example                       # 环境变量模板（复制为 .env 填写）
│   └── requirements.txt
└── frontend/                              # Vue3 前端
    ├── src/
    │   ├── api/                           # fetch 封装 + SSE 流式解析
    │   ├── stores/                        # auth / chat / theme（Pinia）
    │   ├── components/                    # TopNav / SessionSidebar / ParamPanel / MarkdownView 等
    │   └── views/                         # 首页 / 对话 / 生图 / 解析 / 关于 / 登录 / 注册 / 用户中心
    └── package.json
```

## 启动方式

### 1. 数据库

MySQL 8.0 服务运行后，创建数据库（表结构由后端启动时自动创建）：

```sql
CREATE DATABASE IF NOT EXISTS ai_assistant DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 后端（FastAPI，端口 8000）

```bash
cd backend
python -m venv .venv                     # 首次
.venv\Scripts\python -m pip install -r requirements.txt   # 首次
copy .env.example .env                   # 首次：填写 DATABASE_URL / JWT_SECRET / LLM_API_KEY
.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

大模型配置（`backend/.env`）：

```ini
LLM_API_KEY=你的Key        # 填写后流式对话走真实模型
LLM_BASE_URL=https://api.deepseek.com/v1   # 任意 OpenAI 兼容接口
LLM_MODEL=deepseek-chat
MOCK_LLM=false             # 未配置 Key 时保持 true 可使用 mock 流式联调
```

### 3. 前端（Vite，端口 5173）

```bash
cd frontend
pnpm install               # 首次（包管理器统一用 pnpm）
pnpm dev                   # 本地开发，/api 自动代理到 8000
```

生产构建：`pnpm build`，预览：`pnpm preview`。

## 多模型接入（各类 OpenAI + 本地大模型）

系统内置"大模型服务商"管理，任何 OpenAI 兼容接口（云端厂商、本地 Ollama / vLLM / LM Studio 等）都可接入：

1. **设置页 → 大模型设置**：已预置 DeepSeek（云端）与本地 Ollama 两个服务商；点「添加服务商」填入名称、Base URL（云端如 `https://api.xxx.com/v1`，本地如 `http://127.0.0.1:11434/v1`）与模型列表即可。
2. **API Key**：点击服务商行选中后「API Key」按钮亮起，点击即可粘贴保存；Key 仅存后端 `providers.json`，前端只显示"已配置/未配置"。本地服务无需 Key。
3. **选择模型**：对话页输入框左侧选择器 —— 未选择显示 **+**，选择后以亮蓝色显示模型名；发送时后端按所选服务商转发（未配 Key 的云端服务会在对话中明确提示）。
4. **测试调用**：设置页每个服务商带「测试」按钮，用默认模型发一条真实流式请求并显示结果。

服务商接口：`GET/POST /api/providers`、`PATCH/DELETE /api/providers/{id}`、`POST /api/providers/{id}/api-key`（空串清除）。

## 验证

- 后端接口回归：`cd backend && .venv\Scripts\python smoke_test.py`（覆盖注册/登录/会话 CRUD/SSE 流式/文件解析等 16 项断言）。
- 端到端：浏览器打开 `http://localhost:5173`，注册登录后即可对话；上传 TXT/Markdown/PDF 可基于文档提问；会话与消息实时落库，刷新不丢失。

## 已知边界（首期）

- 大模型 API Key 未配置时对话为 Mock 流式输出（联调用）。
- AI 绘图模型选型待定，`POST /api/draw/generate` 已预留，未配置 `DRAW_API_KEY` 时返回 503 与提示。
- 文件解析：单文件 ≤10MB、PDF ≤50 页、超长截断至 20 万字符；扫描件（图片型 PDF）首期不支持。
