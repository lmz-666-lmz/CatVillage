<p align="center">
  <img src="https://img.shields.io/badge/version-2.3-blue?style=flat-square" alt="Version 2.3">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License MIT">
  <img src="https://img.shields.io/badge/Vue-3.5-brightgreen?style=flat-square&logo=vue.js" alt="Vue 3.5">
  <img src="https://img.shields.io/badge/FastAPI-latest-009688?style=flat-square&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/MySQL-8.0+-4479A1?style=flat-square&logo=mysql" alt="MySQL 8.0+">
</p>

<h1 align="center">🐱 猫村 APP — CatVillage</h1>

<p align="center">
  <strong>一个专注于猫咪社交、健康管理与情感分析的综合性智能平台</strong>
  <br>
  基于 Vue 3 + FastAPI + MySQL + DeepSeek AI 的全栈项目
</p>

---

## 📑 目录

- [快速开始](#-快速开始)
- [系统概述](#-系统概述)
- [分层架构](#-系统分层架构)
- [业务模块](#-业务模块)
- [V2.3 核心特性](#-v23-核心特性)
- [V2.2 核心特性](#-v22-核心特性)
- [技术栈](#-技术栈)
- [项目结构](#-项目结构)
- [部署说明](#-部署说明)
- [安全提示](#-安全提示)

---

## 🚀 快速开始

### 环境要求

| 工具 | 版本 |
|------|------|
| Python | 3.10+ |
| Node.js | 20+（推荐 22+） |
| MySQL | 8.0+ |

### 1. 克隆项目

```bash
git clone https://github.com/your-username/CatVillage.git
cd CatVillage
```

### 2. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入你的数据库连接信息、DeepSeek API Key 等
```

`.env` 配置说明：

```env
# 数据库连接（MySQL）
DATABASE_URL=mysql+pymysql://catvillage_user:your-db-password@127.0.0.1:3306/catvillage?charset=utf8mb4

# AI 大模型（DeepSeek）
AI_API_KEY=你的-DeepSeek-API-Key
AI_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-chat

# 管理员账号（首次启动自动创建）
ADMIN_USERNAME=admin
ADMIN_PASSWORD=你的-管理员-密码

# JWT 密钥（务必修改为随机字符串）
SECRET_KEY=至少32位的随机字符串-请替换

# 跨域白名单
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# 数据库连接池（低配服务器推荐配置）
DB_POOL_SIZE=3
DB_MAX_OVERFLOW=2
DB_POOL_RECYCLE=1800

# 上传文件大小上限（字节）
UPLOAD_MAX_BYTES=10485760
```

### 3. 安装依赖 & 启动后端

```bash
cd backend
pip install -r requirements.txt

# 首次启动会自动建表并创建管理员账号
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

后端启动后访问 http://127.0.0.1:8000/docs 查看 Swagger API 文档。

### 4. 安装依赖 & 启动前端

```bash
cd frontpoint
npm install
npm run dev
```

前端默认运行在 http://localhost:5173。

### 5. 默认管理员账号

| 字段 | 值 |
|------|-----|
| 用户名 | `admin` |
| 密码 | 你在 `.env` 中设置的 `ADMIN_PASSWORD` |

> ⚠️ **生产环境上线后必须立即修改管理员密码！**

---

## 📖 系统概述

猫村APP 是一个专注于猫咪社交、健康管理与情感分析的综合性智能化平台，采用前后端分离架构，深度集成机器学习（声音识别）、计算机视觉（图像情绪识别）与大语言模型（AI 对话）能力。

**V2.0 核心升级**：视觉情绪识别与视听融合分析、专业医生咨询模块、后台管理系统、健康综合评分引擎、文件上传存储服务、投喂记录追踪、系统设置中心。

**V2.2 正式版**：V2.2 在 V2.0 基础上重点完善了移动端交互、AI 养育助手、消息删除、情绪记录管理、后台管理与热门话题能力。

**V2.3 正式版**：V2.3 聚焦资源安全清理、AI 上下文深度整合、年龄校验规范化与设置/登录/欢迎页体验升级。

---

## 🏗 系统分层架构

### 前端应用层 (Client Layer)

| 技术 | 用途 |
|------|------|
| Vue 3 (Composition API) | 核心框架，类型安全与逻辑复用 |
| Vite | 极速本地冷启动与 HMR 热更新 |
| Vant 4 | 移动端优先的响应式 UI 组件库 |
| Tailwind CSS 4 | 原子化样式 |
| Pinia 3 | 模块化状态管理（`user`, `cats`, `currentCat`） |
| Vue Router 5 | SPA 路由，25+ 路由页面，懒加载 |

### 后端服务层 (Service Layer)

| 技术 | 用途 |
|------|------|
| FastAPI | 原生异步支持，自动生成 OpenAPI/Swagger 文档 |
| SQLAlchemy ORM | 数据库抽象层 |
| Pydantic | 请求/响应数据严格类型校验 |
| JWT (python-jose) + bcrypt | 无状态鉴权与密码哈希 |
| StorageService | 文件上传校验、分类存储 |

### 数据与算法底层 (Infrastructure Layer)

- **数据库**：MySQL 8.0+，`utf8mb4` 字符集，连接池优化
- **ML 引擎**：scikit-learn 模型 (`cat_emotion_model.pkl`) 用于猫叫声情绪识别
- **AI 大模型**：DeepSeek API，支持热更新配置（无需重启）
- **视觉识别**：轻量级规则启发式匹配（低配服务器友好）

---

## 📦 业务模块

| 领域模块 | 前端 | 后端 | 核心职责 |
|:---|:---|:---|:---|
| **Auth** 鉴权 | `LoginView`, `RegisterView` | `auth.py` | 注册、登录、JWT Token 签发 |
| **Pet Profiles** 档案 | `MyPetsView`, `AddCatView`, `EditCatView`, `CatArchiveView` | `pet_profiles.py` | 宠物全生命周期档案维护 |
| **Emotions** 情感分析 | `EmotionsView`, `MeowRecordDetailView`, `AudioHistoryView` | `emotions.py` | 音频特征提取、ML 推理、情绪报表 |
| **Vision** 🆕 视觉识别 | `api/vision.ts` | `vision.py` | 图像情绪识别、视听融合分析 |
| **AI Assistant** 智能助理 | `AIAssistantView` | `ai_assistant.py` | 上下文感知的 AI 对话 |
| **Health** 健康监测 | `FeedRecordView`, `CatArchiveView` | `health.py` | 体重追踪、投喂记录、综合评分 |
| **Doctors** 🆕 专业医生 | `ProfessionalDoctorsView` | `doctors.py` | 兽医在线咨询、就诊贴士 |
| **Social** 猫村社区 | `SocialView`, `SocialDetailView`, `CreatePostView`, `SocialSearchView` | `social.py` | 图文动态流、点赞、评论、收藏 |
| **Message** 即时消息 | `MessagesView`, `ChatDetailView`, `AddFriendView` | `message.py` | 点对点私信通讯 |
| **Admin** 🆕 后台管理 | `AdminDashboardView` | `admin.py` | 全量数据管理、AI 配置热更新 |
| **Settings** 🆕 系统设置 | `SettingsView` | — | 通知与隐私偏好管理 |
| **User Profile** 个人中心 | `UserProfileView` | — | 个人资料展示与编辑 |

> 🆕 = V2.0 新增模块

---

## ✨ V2.3 核心特性

### 🧹 资源安全清理机制
- 新增 `safe_delete_file` 安全删除工具，仅允许删除 `storage/` 和 `uploads/` 目录内的项目文件，杜绝路径穿越风险
- 删除猫咪档案时自动清理：关联的情绪记录、投喂记录、体重记录，以及头像和音频物理文件
- 删除情绪/叫声记录时同步删除对应的音频文件，释放磁盘空间
- 删除社区动态时同步清理上传的图片文件，避免残留
- 管理后台删除操作同样触发资源清理，全链路覆盖

### 🤖 AI 养育助手深度整合
- AI 对话上下文自动注入最近 5 条喵喵台情绪记录，让建议更有数据支撑
- 猫咪卡片新增情绪参考提示行（"已参考最近 N 条喵喵台记录"），上下文透明可见
- 移除前端强制截断 prompt 后缀，让 AI 模型自行组织回答节奏，回复更自然
- 未选择猫咪时隐藏聊天区域和输入栏，交互更清晰

### 🐱 年龄输入校验规范化
- 新增 `validateAgeInput` 校验函数，支持"X岁X个月"格式的实时校验
- 添加/编辑猫咪页面增加输入提示文案（"例如：2岁、6个月、2岁3个月，留空表示年龄未知"）
- 非法格式时输入框红框高亮 + 错误提示，提交时再次拦截
- 年龄范围限制 0-30 岁，防止异常数据

### ⚙️ 设置页体验升级
- 新增退出登录按钮，一键清除登录态与本地缓存
- 新增"当前版本 V2.3"入口，点击弹出版本更新内容介绍
- 后台管理入口仅对管理员可见，普通用户不再看到无法访问的入口
- 用户名修改弹窗改为自定义毛玻璃遮罩样式，视觉效果更精致
- 保存按钮从固定悬浮改为跟随页面流，适配不同屏幕高度

### 🎨 界面细节优化
- 登录页与欢迎页整体布局更紧凑，减小 Logo 尺寸与间距，一屏展示更完整
- 喵喵台空状态升级为动画猫咪表情 + 浮动猫爪，引导添加猫咪更生动
- 专业医生"视频咨询"卡片标注"演示功能"，明确功能阶段
- 管理后台统计面板新增"热点话题"和"配置"入口，导航更全面
- 投喂记录年龄展示修复 `null` 值处理，避免显示异常

> 以上特性在 V2.2 已有能力基础上增量迭代。

---

## ✨ V2.2 核心特性

### 🐱 猫咪年龄统一修复
- 年龄统一按月龄存储，支持岁/月自动换算展示
- 未填写年龄时统一显示"年龄未知"，告别混乱的默认值

### 🤖 AI 养育助手优化
- 猫咪卡片可手动收缩，释放聊天视野
- 快捷功能改为横向 chips，操作更直观
- 回答更精简，聚焦核心养育建议

### 🎙 喵喵台体验增强
- 移动端录音能力检测，不支持时自动隐藏录音按钮
- 支持上传音频文件兜底，适配更多设备
- 支持删除情绪/叫声记录，方便管理历史数据

### 🏘 社区广场优化
- 村长推荐帖置顶展示，优质内容不沉底
- 热门话题基于真实互动数据聚合，而非静态标签
- 点赞/收藏交互逻辑统一，体验一致

### 💬 消息体验优化
- 聊天记录列表支持轮询自动刷新
- 进入聊天页面默认滚动到底部（最新消息）
- 支持仅删除自己这边的聊天记录，对话管理更灵活

### 🛡 后台管理增强
- 现代化 UI 改版，操作更流畅
- 村长推荐管理、用户密码重置
- 热门话题管理、真实数据统计看板

### 📱 移动端视觉修复
- 未设置头像时使用本地 SVG 默认头像，无需外部请求
- AI/聊天页面固定头部和底部输入栏，滚动区域独立
- TabBar 遮挡内容问题修复，页面可滚动区域完整

### 🖥 服务器部署优化
- 低配服务器增加 Swap 配置指引，降低 OOM 风险
- Nginx 残留配置自动清理，避免端口冲突
- 后端内存占用优化，适配学生机等低配环境

> 以上特性在 V2.0 已有能力（视觉识别、健康评分、医生模块、文件存储、投喂记录等）基础上增量迭代。

---

## 🛠 技术栈

| 层级 | 技术 | 版本 |
|:---|:---|:---|
| 前端框架 | Vue 3 (Composition API) | 3.5 |
| 构建工具 | Vite | 8.x |
| 类型系统 | TypeScript | 6.0 |
| UI 框架 | Vant | 4.9 |
| 原子化 CSS | Tailwind CSS | 4.2 |
| 状态管理 | Pinia | 3.0 |
| 路由 | Vue Router | 5.0 |
| HTTP 客户端 | Axios | 1.14 |
| 后端框架 | FastAPI | latest |
| ORM | SQLAlchemy | latest |
| 数据校验 | Pydantic | latest |
| 数据库 | MySQL | 8.0+ |
| 认证 | JWT (python-jose) + bcrypt | — |
| AI 模型 | DeepSeek API | 可配置 |
| ML 引擎 | scikit-learn | latest |
| 单元测试 | Vitest | 4.x |
| E2E 测试 | Playwright | 1.58 |
| 代码检查 | ESLint + Oxlint | 10.x |
| 代码格式化 | Prettier | 3.8 |

---

## 📁 项目结构

```
CatVillage/
├── backend/                        # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/                 # API 路由层 (10 个模块)
│   │   │   ├── admin.py            # 🆕 后台管理
│   │   │   ├── ai_assistant.py     # AI 对话
│   │   │   ├── auth.py             # 认证
│   │   │   ├── doctors.py          # 🆕 专业医生
│   │   │   ├── emotions.py         # 情绪识别
│   │   │   ├── health.py           # 健康管理
│   │   │   ├── message.py          # 即时消息
│   │   │   ├── pet_profiles.py     # 宠物档案
│   │   │   ├── social.py           # 社交动态
│   │   │   └── vision.py           # 🆕 视觉识别
│   │   ├── core/                   # 核心基础设施
│   │   │   ├── config.py           # 配置管理
│   │   │   ├── dependencies.py     # 依赖注入 & JWT 拦截
│   │   │   ├── model_service.py    # ML 模型服务
│   │   │   ├── security.py         # 密码哈希 & Token 生成
│   │   │   └── storage.py          # 🆕 文件上传存储
│   │   ├── database/               # 数据库会话 & 自动建表
│   │   │   ├── session.py          # SQLAlchemy 引擎
│   │   │   └── bootstrap.py        # 自动建表 & 管理员种子
│   │   ├── models/                 # SQLAlchemy ORM 模型 (8 个实体)
│   │   └── schemas/                # Pydantic 校验模式
│   ├── scripts/
│   │   └── init_mysql.py           # 手动初始化脚本
│   ├── uploads/                    # 上传文件存储目录
│   ├── .env.example                # 环境变量模板
│   ├── requirements.txt
│   └── main.py                     # 应用入口
├── frontpoint/                     # Vue 3 前端
│   └── src/
│       ├── api/                    # API 请求层 (12 个模块)
│       ├── components/             # 可复用组件
│       ├── composables/            # 组合式函数 (7 个)
│       ├── constants/              # 常量定义
│       ├── router/                 # 路由配置 (26 条路由)
│       ├── stores/                 # Pinia 状态管理
│       ├── types/                  # TypeScript 类型定义
│       ├── utils/                  # 工具函数
│       └── views/                  # 页面视图 (27 个)
├── deploy/                         # 部署配置
│   ├── catvillage-backend.service  # Systemd 服务文件
│   └── nginx-catvillage.conf       # Nginx 反向代理配置
└── README.md
```

---

## 🚢 部署说明

### 低配服务器优化（阿里云等学生机）

针对低配云服务器极易 OOM 的痛点：

- **Swap 虚拟内存**：挂载 2GB-4GB Swap 缓存区，应对 ML 模型加载峰值
- **Workers 限制**：Uvicorn 强制 `workers=1`，防止多进程耗尽内存
- **数据库连接池**：`DB_POOL_SIZE=3`、`DB_MAX_OVERFLOW=2`、`DB_POOL_RECYCLE=1800`

### 部署文件

`deploy/` 目录提供了：

| 文件 | 用途 |
|------|------|
| `catvillage-backend.service` | Systemd 服务，实现开机自启和进程守护 |
| `nginx-catvillage.conf` | Nginx 反向代理，处理静态资源和 API 转发 |

### 部署步骤概览

1. 服务器安装 Python 3.10+、Node.js 20+、MySQL 8.0+、Nginx
2. 克隆项目到 `/opt/catvillage/`
3. 配置 `backend/.env`（填入生产环境数据库密码和密钥）
4. 安装后端依赖，配置 Systemd 服务
5. 构建前端 `npm run build`，配置 Nginx
6. 启动服务：`systemctl start catvillage-backend`

---

## 🔒 安全提示

```text
⚠️  .env 文件严禁提交到 GitHub（已在 .gitignore 中排除）
⚠️  .env.example 只能放占位符，不要写真实密码或密钥
⚠️  SECRET_KEY 务必使用至少 32 位的随机字符串
⚠️  真实 DeepSeek API Key 只放在本地 .env 或服务器环境变量中
⚠️  生产环境部署后立即修改所有默认密码
⚠️  定期更新依赖，关注安全公告
```

### 密码安全

- 密码使用 `passlib[bcrypt]` 加盐哈希存储，数据库不存明文
- JWT Token 基于 `python-jose[cryptography]` 签发，无状态鉴权
- 管理接口前后端双重校验（前端路由守卫 + 后端 `require_admin`）

### AI 调用安全

- API Key 仅通过 `.env` 注入，源码中无硬编码
- DeepSeek R1 的 `<think>` 标签后端正则清洗，防止 DOM 污染
- AI 接口异常时自动降级返回友好提示，杜绝前端白屏

---

## 📄 版本历史

| 版本 | 日期 | 核心变更 |
|:---|:---|:---|
| **V2.3** | 2026-07 | 🧹 正式稳定版：资源安全清理机制（`safe_delete_file`、删除档案/记录/动态时同步清理物理文件）；AI 上下文注入最近 5 条喵喵台情绪记录；年龄输入实时校验与红框提示；设置页退出登录、版本介绍弹窗、管理员入口过滤；登录/欢迎页紧凑布局；喵喵台空状态动画升级；管理后台统计面板扩展；投喂记录 null 值修复 |
| **V2.2** | 2026-07 | 🐱 正式稳定版：猫咪年龄按月龄统一修复；AI 养育助手卡片收缩与快捷 chips；喵喵台移动端录音检测与音频上传兜底；情绪/叫声记录删除；社区广场村长推荐置顶与热门话题真实聚合；消息轮询刷新、默认滚动到底部、仅自删聊天记录；后台管理 UI 现代化、村长推荐/密码重置/热门话题/真实统计；移动端默认头像本地 SVG、固定头部底部、TabBar 遮挡修复；低配服务器 Swap/内存优化 |
| V2.1 | 2026-07 | 小幅修复版本，相关改动已合并进 V2.2 |
| **V2.0** | 2026-07 | 视觉情绪识别与视听融合；健康综合评分引擎；后台管理系统；专业医生；文件上传存储；投喂记录追踪；系统设置；Tailwind CSS；依赖大版本升级 |
| V1.0 | 2025 | 核心社交与情绪分析平台：用户认证、宠物档案、音频情绪识别、AI 对话、社交动态流、即时消息 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📝 开源协议

本项目基于 MIT 协议开源。详见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  <sub>Made with ❤️ for cats everywhere 🐱</sub>
</p>
