# AGENTS.md

> 本文件给 AI 编程助手（Cursor / Claude Code 等）和新加入的开发者看，快速了解项目是什么、有什么技术栈硬约束、哪些决策已定不可推翻。

## 1. 项目是什么

轻量AI助手Web端 —— 面向学生、开发者、办公人群的轻量化在线AI工作台。支持流式 AI 对话、代码高亮、文档解析、AI 绘图、账号体系。

- 产品需求：`PRO.md`
- 技术选型与关键决策：`TECH_DESIGN.md`

## 2. 技术栈硬约束

| 类别 | 必须用 | 禁止 |
| --- | --- | --- |
| 前端 | Vue3 + TailwindCSS + Pinia（状态管理） | React / Vue2 / 其他前端框架 |
| UI 组件 | 纯 Tailwind 手写组件，不引入组件库 | Element Plus / Naive UI / Ant Design Vue 等组件库 |
| 后端 | Python FastAPI | Django / Flask / Node.js 后端 |
| 数据库 | MySQL 8.0 | 擅自改用 SQLite 等（除非明确要求） |
| 鉴权 | JWT（localStorage 或 cookie，7 天记住登录） | 自造明文 / Session 方案 |
| 密码 | bcrypt 哈希后入库 | 明文存储 |
| 样式 | TailwindCSS，冷色系，浅色默认、深色同步，低饱和 | 花哨特效、大面积高饱和艳色 |
| AI 接入 | 经后端转发大模型 API | 前端直连、API Key 暴露到前端 |

## 3. 已确认的关键决策（不要推翻）

1. **会话 / 消息表首期全建**：`user` + `chat_session` + `chat_message` 三表首期同时建立，登录后会话即持久化到 MySQL，不做本地存储。
2. **文件解析跑通优先**：PDF 用 PyMuPDF 提取文本，TXT / Markdown 直接读原文；单文件 ≤10MB、≤50 页；不做 RAG，短文档直接进上下文、超长截断；首期不支持扫描件（图片型 PDF）。
3. **保留完整前后端分离全栈架构**：不因"轻量"定位砍掉后端；大模型 / 绘图 API Key 仅存后端。

详见 `TECH_DESIGN.md` 第 7 节。

## 4. 待定项（不要擅自假设）

- AI 绘图模型 API 选型未定，仅预留接入接口。
- 二期再考虑：扫描件 OCR、表格结构解析、更多文件格式、头像上传。

## 5. 运行与构建命令

前端（Vue3 + Vite，包管理器统一用 **pnpm**，禁止 npm / yarn）：

```bash
pnpm install     # 安装依赖
pnpm dev         # 本地开发（热更新）
pnpm build       # 构建生产版本
pnpm preview     # 本地预览构建产物
```

后端（Python FastAPI，在 backend 目录下操作）：

```bash
python -m venv .venv                                 # 首次：创建虚拟环境
.venv\Scripts\python -m pip install -r requirements.txt  # 首次：安装依赖
copy .env.example .env                                # 首次：填写数据库与 API 配置
.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000  # 启动（启动时自动建表）
.venv\Scripts\python smoke_test.py                   # 后端接口回归测试（16 项断言）
.venv\Scripts\python providers_test.py               # 大模型服务商接口测试（13 项断言）
```

## 6. 大模型多源接入（已上线，勿回退设计）

- **任意 OpenAI 兼容服务 + 本地模型**统一管理：`backend/providers.json`（gitignore，内含各平台 API Key，仅存后端；列表接口只返回 `api_key_configured`，永不回传明文）。
- 服务商接口：`GET/POST /api/providers`、`PATCH/DELETE /api/providers/{id}`、`POST /api/providers/{id}/api-key`（空串清除 Key）。
- 对话：`POST /api/chat/stream` 的 ChatRequest 含 `provider_id`；未传时回退 `.env` 的 LLM_* 全局配置（Mock 兜底）。云端服务商未配 Key → SSE `error` 事件提示去设置页配置；本地地址（127.0.0.1/localhost）免 Key。
- 预置三个服务商：DeepSeek（云端）、本地微调模型 MiniMind-768（`http://127.0.0.1:8001/v1`）、本地 Ollama（http://127.0.0.1:11434/v1）。
- 前端入口：对话页输入框左侧模型选择器（未选显示 +、选中亮蓝显示模型名）；设置页「大模型设置」横条负责服务商增删改、API Key 添加与测试调用；「模型参数」横条调温度等。

后端接口冒烟测试位于 `backend/smoke_test.py`，改动后端后应跑通 16 项断言。
