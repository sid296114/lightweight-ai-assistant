# 轻量AI助手Web端 产品需求文档

文档版本：V1.0

产品定位：面向学生、开发者、办公人群的轻量化在线AI工作台

# 1 产品概述

## 1.1 产品背景

面向日常办公、学习、开发场景，打造一款轻量化、上手简单的网页版AI助手。不堆砌繁杂功能，优先保证对话流畅度、代码渲染、文件解析能力，界面干净清爽，降低视觉疲劳。

## 1.2 目标用户

- 学生：文案撰写、习题答疑、思路梳理。
- 开发者：代码生成、bug排查、代码解释。
- 办公人员：文档总结、方案撰写、信息整理。

## 1.3 产品目标

- 提供稳定的流式AI对话体验，支持Markdown、代码高亮展示。
- 支持文档上传解析、AI文生图。
- 界面简约精美，浅色调为主，低饱和冷色主调，视觉舒适。
- 响应式布局，优先适配PC端，兼容平板访问。

## 1.4 非目标（首期不做）

- 不做复杂的社群、付费会员体系。
- 不支持超大文件（单文件上限在开发阶段定义）。
- 不做重度3D、炫酷动效，保持极简风格。

# 2 核心功能

功能模块划分：导航模块、会话管理模块、AI对话模块、文件解析模块、AI绘图模块、模型参数配置模块、账号登录注册模块、关于页模块。

## 2.1 顶部导航栏

- 导航菜单：首页、AI对话、AI生图、文档解析、关于。
- 右上角：登录/注册入口、浅色/深色模式切换开关。
- 交互：当前页面菜单高亮，点击跳转对应页面。

## 2.2 左侧会话列表（可折叠侧边栏）

- 新建会话：点击创建全新对话。
- 会话列表展示：会话标题、创建时间。
- 会话操作：重命名会话、删除会话。
- 折叠功能：支持收起侧边栏，扩大中间内容区域。
- 本地存储：会话记录默认保存在浏览器本地（首期）。

## 2.3 中间主对话区（核心区域）

- 流式输出：AI回复逐字流式打字效果，支持停止生成。
- 消息气泡区分：用户消息、AI回复消息样式区分。
- Markdown渲染：标题、列表、引用、表格正常渲染。
- 代码块渲染：代码高亮、一键复制代码按钮、语言标识。
- 加载状态：AI生成中展示柔和加载动画。
- 错误提示：调用失败、超时给出友好提示文本。
- 滚动：自动滚动到最新消息。

## 2.4 底部输入区域

- 多行文本输入框，支持换行，自动增高。
- 发送按钮：提交提问。
- 快捷按钮：文件上传按钮、快速生图按钮。
- 输入限制：支持输入字数上限提示。

## 2.5 文件上传与文档解析功能

- 支持格式：TXT、Markdown、PDF（首期）。
- 能力：上传文档后，AI读取文档内容，基于文档进行问答、总结、提取要点。
- 限制：单文件大小限制，上传中进度提示。
- 交互：上传成功后，在对话区提示文档已加载，可基于文档提问。

## 2.6 AI绘图模块

- 独立页面：AI生图工作台。
- 提示词输入：正向提示词输入框、反向提示词输入框。
- 参数：图片尺寸、生成数量。
- 生成记录：保存本次生成图片，支持图片下载。
- 生成状态：排队、生成中、生成完成、失败提示。

## 2.7 右侧模型参数面板（可收起）

- 模型选择：下拉切换接入的大模型。
- 温度（temperature）：滑块控制创造性。
- 最大生成长度：滑块控制单次回复token上限。
- 重置按钮：一键恢复参数默认值。
- 面板支持收起，给对话区域更大空间。

## 2.8 账号登录与注册模块（MySQL）

该模块使用MySQL 8.0存储用户账号信息，为P0级需求。

### 2.8.1 注册功能

- 支持用户名、邮箱、密码注册。
- 校验：邮箱格式、用户名长度、密码强度。
- 密码禁止明文存储，后端使用bcrypt哈希加密后写入MySQL。
- 重复邮箱/用户名校验，给出提示。

### 2.8.2 登录功能

- 支持邮箱+密码登录。
- 登录成功下发JWT token，前端存储在localStorage或cookie。
- 记住登录状态选项（有效期7天）。
- 错误提示：账号不存在、密码错误。

### 2.8.3 用户中心（简易版）

- 查看账号信息：用户名、邮箱、注册时间。
- 修改密码（校验旧密码）。
- 退出登录：清除本地token，跳转登录页。

### 2.8.4 权限控制

- 未登录：仅可访问登录、注册页，无法使用AI对话、生图、文件解析等功能。
- 已登录：会话记录首期可选本地存储；二期迁移到MySQL，与用户ID关联实现云端漫游。

### 2.8.5 安全规则

- 密码长度最少6位。
- 防暴力破解：后端做简单的频率限制。
- 登录请求必须走HTTPS传输。

## 2.9 关于页面

- 产品简介。
- 技术栈说明：前端Vue3 + TailwindCSS，后端Python FastAPI，接入大模型API，流式输出。
- 版本信息。
- 免责提示。

## 2.10 基础通用能力

- 深色/浅色主题切换：浅色为默认，主色调统一为冷色系；深色模式同步冷色体系。
- 响应式：PC端三栏布局；平板端自动收起侧边栏和参数面板。
- 复制功能：消息、代码块一键复制，复制成功轻提示。

# 3 设计要点

## 3.1 色彩规范

- 基础基调：浅色调为主，页面背景为#FAFBFD（极浅灰白）。
- 主色调：低饱和冷冰蓝色#6495ED（冷色系，不刺眼，科技感柔和）。
- 辅助色：浅灰#86909C、成功绿#52C41A、警告橙#FF7D00、错误红#F53F3F。
- 文字色：主文字#1D2129、次要文字#4E5969、占位文字#86909C。
- 卡片底色：#FFFFFF。
- 规则：高饱和度颜色仅用于状态提示，大面积不用艳色；深色模式底色#111827，主色沿用同色系冷蓝，降低明度适配暗色环境。

## 3.2 版式与布局

- 布局结构：经典三栏布局。左侧会话侧边栏（固定宽度，可折叠）；中间对话主区（弹性宽度，核心视觉）；右侧模型参数面板（固定宽度，可折叠）。
- 留白策略：充足留白，拒绝拥挤；卡片间距统一，呼吸感强。
- 圆角：全局统一圆角8px，卡片、输入框、按钮统一。
- 阴影：轻薄柔和阴影（0 2px 12px rgba(0,0,0,0.06)），禁止厚重深色阴影。
- 字体：无衬线字体（Inter/系统思源黑体），层级清晰。标题16px/600，正文14px/400，辅助文字12px/400。

## 3.3 组件设计规范

- 按钮：填充主色按钮、文字按钮、幽灵按钮三种；hover有轻微透明度变化，无夸张动效。
- 输入框：浅底色边框，聚焦时主色边框高亮。
- 消息气泡：用户消息浅冷蓝底色，AI消息白色卡片底色，区分清晰。
- 代码块：深色代码背景，代码高亮配色柔和，右下角复制图标。
- 滑块、下拉：简约样式，和整体冷色风格统一。

## 3.4 动效与交互规范

- 原则：克制、轻量化，不花哨，拒绝赛博朋克、流光等特效。
- 流式打字动画：平缓逐字输出。
- 过渡动画：面板展开收起、弹窗淡入淡出，时长200ms。
- 反馈：复制成功、上传成功、提交成功使用轻toast提示，无弹窗强打扰。
- 加载动画：简约线性加载，不使用复杂旋转动画。

## 3.5 风格总原则

简约、精美、干净、专业、轻科技感；优先保证阅读和使用舒适度，视觉上安静克制，适合长时间办公学习使用。

# 4 数据库设计（MySQL 8.0）

首期核心为用户登录信息表user；会话与消息表为二期扩展（实现云端会话存储时启用）。

## 4.1 user 用户表（核心，存储登录信息）

```sql
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户主键ID',
  `username` varchar(50) NOT NULL COMMENT '用户名，唯一',
  `email` varchar(100) NOT NULL COMMENT '登录邮箱，唯一',
  `password_hash` varchar(255) NOT NULL COMMENT 'bcrypt加密后的密码，不存明文',
  `avatar` varchar(255) DEFAULT '' COMMENT '头像地址，预留',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '账号状态：1正常 0禁用',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '信息更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户账号表';
```

字段说明：password_hash永远存储哈希字符串，前端传原始密码，后端bcrypt加密后入库；utf8mb4支持emoji与特殊字符；唯一索引保证用户名、邮箱不能重复注册。

## 4.2 chat_session 会话表（二期扩展，预留）

```sql
CREATE TABLE `chat_session` (
  `id` bigint AUTO_INCREMENT PRIMARY KEY,
  `user_id` bigint NOT NULL COMMENT '关联user.id',
  `title` varchar(100) NOT NULL COMMENT '会话标题',
  `model_name` varchar(50) DEFAULT '' COMMENT '选用模型',
  `temperature` float DEFAULT 0.7,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 4.3 chat_message 消息表（二期扩展，预留）

```sql
CREATE TABLE `chat_message` (
  `id` bigint AUTO_INCREMENT PRIMARY KEY,
  `session_id` bigint NOT NULL COMMENT '关联会话id',
  `role` varchar(20) NOT NULL COMMENT 'user / assistant',
  `content` longtext NOT NULL COMMENT '消息内容',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  KEY `idx_session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

# 5 技术栈

| 层次 | 技术选型 |
| --- | --- |
| 前端 | Vue3 + TailwindCSS |
| 后端 | Python FastAPI |
| 数据库 | MySQL 8.0 |
| 鉴权 | JWT |
| 密码加密 | bcrypt |
| AI能力 | 大模型API、SSE流式输出、文件解析、AI绘图 |

# 6 交互优先级（P0/P1/P2）

| 优先级 | 范围 |
| --- | --- |
| P0 | 登录注册、MySQL user表、JWT鉴权、流式对话、会话本地存储、Markdown渲染、代码高亮 |
| P1 | AI绘图、文件解析、参数调节面板、关于页 |
| P2 | 云端会话存储（chat_session + chat_message表）、头像上传、更多文件格式 |

# 7 风险与备注

- 文件解析能力依赖后端解析服务，首期优先支持PDF/TXT。
- 流式效果依赖后端SSE流式接口。
- 图片生成依赖绘图模型API。
