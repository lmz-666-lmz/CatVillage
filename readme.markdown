# 猫村APP

**文档版本**：V1.0  
**系统名称**：猫村 (Cat Village)
**架构负责人**：明哲

---

## 1. 系统概述

“猫村APP”是一个专注于猫咪社交、健康管理与情感分析的综合性智能化平台。系统采用标准的前后端分离架构，并深度集成了机器学习（声音识别）与大语言模型（AI对话）能力。

考虑到 V1.0 版本的正式部署环境受限于**阿里云学生机**（低内存、单核CPU配置），本文档旨在从工程标准出发，规范系统的全栈物理架构、逻辑架构、低资源环境调优机制以及核心研发规范，为研发团队提供全局性的技术指导。

---

## 2. 系统总体分层架构

系统架构设计遵循“高内聚、低耦合”的原则，整体分为展示层、网关/服务层、业务逻辑层与数据/算法底层：

### 2.1 前端应用层 (Client Layer)
基于现代 Web 工程化标准构建的高性能 SPA（单页应用）：
* **核心框架**：Vue 3 (Composition API) + TypeScript 确保类型安全与逻辑复用。
* **构建流**：Vite 提供极速的本地冷启动与 HMR（热更新）。
* **UI 与交互**：Vant 组件库提供移动端优先的丝滑响应式体验。
* **状态总线**：Pinia 划分模块化状态树（`user`, `cats`, `currentCat`），精准控制多实例宠物数据的响应式流转。

### 2.2 后端服务层 (Service Layer)
基于高性能异步框架构建的 RESTful 微服务化单体架构：
* **核心框架**：FastAPI 提供原生异步支持与自动化的 OpenAPI/Swagger 接口文档生成。
* **路由分发**：通过 `APIRouter` 按业务域划分子路由 (`/api/v1/auth`, `/api/v1/emotions` 等)。
* **依赖注入**：利用 FastAPI 的 `Depends` 机制实现跨线程的数据库会话管理、JWT 鉴权拦截等横向切面逻辑 (`dependencies.py`)。

### 2.3 数据与模型基础设施 (Infrastructure Layer)
* **持久化**：采用 SQLAlchemy ORM 提供数据库无关的操作抽象（支持 SQL Server 与 SQLite 动态切换）。
* **数据校验**：Pydantic Schemas 承担数据进出后端的严格类型校验屏障。
* **算法引擎**：集成 `scikit-learn` 模型 (`cat_emotion_model.pkl`) 用于离线的本地机器学习推断（猫叫声识别）；同时通过兼容 SDK 对接 **DeepSeek API** 提供大模型对话能力。

---

## 3. 领域驱动设计 (DDD) 核心业务模块划分

为防止代码劣化，前后端模块进行了严格对齐的领域划分：

| 领域模块 (Domain) | 前端实现 (Views/Composables/API) | 后端实现 (Routes/Models/Schemas) | 核心职责 |
| :--- | :--- | :--- | :--- |
| **Auth** (鉴权中心) | `LoginView`, `RegisterView` | `auth.py`, `user.py` | 用户注册、登录、JWT Token签发与安全校验 |
| **Pet Profiles** (档案管理) | `useCatManagement`, `CatsView` | `pet_profiles.py`, `cat_profile.py` | 宠物全生命周期档案维护，支持多猫咪切换 |
| **Emotions** (情感分析) | `useEmotionAnalysis`, `EmotionsView` | `emotions.py`, `emotion_record.py` | 音频特征提取、本地 ML 模型推理、分析报表 |
| **AI Assistant** (智能助理) | `useAIAssistant`, `AIAssistantView` | `ai_assistant.py`, `ai_chat_history.py`| 上下文感知的 AI 问答对话与历史留存 |
| **Health** (健康监测) | (融合至档案与相关组件中) | `health.py`, `models/health.py` | 体重、疫苗、驱虫等生理指标的跟踪记录 |
| **Social** (猫村社区) | `useSocialFeatures`, `SocialView` | `social.py`, `models/social.py` | 图文动态流 (Feed)、点赞、评论等社交分发逻辑 |
| **Message** (即时消息) | `useMessaging`, `MessagesView` | `message.py`, `models/message.py` | 用户/好友间的点对点私信通讯链路 |

---

## 4. 低配云服务器部署与环境自适应 (Aliyun 适配)

针对阿里云学生机极易发生 OOM (内存溢出) 的痛点，制定以下强制性部署标准：

### 4.1 内存防御与并发限制
* **虚拟内存兜底**：系统初始化时，必须挂载 **2GB - 4GB 的 Swap 缓存区**。算法模型在被 `core/model_service.py` 懒加载时会产生内存峰值，Swap 能以少量 I/O 延迟换取主干 Web 进程的绝对存活。
* **Workers 限制**：生产环境下启动 Uvicorn 时，强制限制 `workers=1` 或 `2`，严禁多进程模型将服务器内存瓜分殆尽。

### 4.2 数据库环境自适应方言切换
* **本地开发环境 (Dev)**：连接 **SQL Server** (`pymssql`)，利用本地电脑的高性能进行复杂建模与全量 Mock 数据压测。
* **生产部署环境 (Prod)**：底层自动降级连接 **SQLite** (`sqlite3`)。零网络配置、单文件存储，将极其有限的 CPU 与内存全量让渡给 Web 业务。*(注：需补充 `connect_args={"check_same_thread": False}` 兼容异步路由)*

---

## 5. 大模型 (DeepSeek) 深度集成与前端容错体系

AI 助理模块已全面接入 DeepSeek。针对“后端调用顺利，前端解析异常”的现象，确立以下排错闭环规范：

* **密钥与网络隔离**：`DEEPSEEK_API_KEY` 必须通过 `.env` 注入。远程调用封装为异步执行单元，设置合理 Timeout。
* **R1 思考标签清洗**：DeepSeek-R1 模型的 `<think>...</think>` 过程会破坏 DOM。后端必须通过正则清洗标签，或将其拆分至独立的 `thinking_process` 字段，严禁前端直接暴力渲染。
* **Markdown 转义防御**：大模型输出包含换行符与代码块转义。前端必须引入 `markdown-it` 等专用解析器，确保安全的富文本渲染，防止抛出 JS 字符串异常。
* **流式截断防护与降级**：小内存服务器处理流式输出 (SSE) 易因 Buffer 溢出导致 JSON 截断。V1.0 建议优先采用非流式调用；后端路由必须包裹全局 `try...except`，在 AI 接口波动时强制返回标准 JSON（如：“猫村村委会的AI信号不太好，请稍后再试喵~”），杜绝前端死机白屏。

---

## 6. 核心工程化设计与机制

### 6.1 全局多态猫咪上下文机制 (Context Switching)
* **痛点**：多猫家庭用户在查看不同爱宠数据时极易发生数据错乱。
* **架构解法**：前端采用 Pinia `currentCat.ts` 状态机。切换猫咪时触发全局事件；各业务 Composable（如 `useEmotionAnalysis`, `useSocialFeatures`）深度监听 `currentCat.id`，变化时自动清理当前缓存并携带新 ID 重新发起 API 请求，实现无感刷新。

### 6.2 前后端解耦与 Mock 联邦
* **架构解法**：建立独立的 Mock 服务层 (`src/mock/`)，全面覆盖所有 API 的返回结构。
* **工程标准**：通过 Vite 环境变量 (`VITE_ENABLE_MOCK=true/false`) 结合底层 `mockHandler.ts`，实现本地网络请求的隐式拦截。前端团队可完全脱离后端 API 进度进行闭环开发。

### 6.3 安全与认证体系 (Security)
* **密码存储**：采用 `passlib[bcrypt]` 进行密码加盐哈希，数据库绝不存储明文。
* **无状态鉴权**：基于 `python-jose[cryptography]` 的 JWT 令牌方案。前端拦截器 (`request.ts`) 统一挂载 Bearer Token，后端通过 `core/security.py` 解析拦截，保障接口防越权访问。

---

## 7. 质量保障与持续集成规范

* **代码风格约束**：前端深度集成 **ESLint** (结合 `oxlint` 提速) 与 **Prettier** (`.prettierrc.json`)；配合工程根目录的 `.editorconfig` 自动抹平跨系统、跨 IDE 的换行符与缩进差异。
* **分级测试策略**：
  * **单元测试 (Unit Test)**：基于 `Vitest` (`vitest.config.ts`) 覆盖工具函数 (`utils/`)、Pinia Store 状态变迁逻辑及核心组件的黑盒断言。
  * **端到端测试 (E2E)**：基于 `Playwright` (`playwright.config.ts`) 编写核心用户旅程（如：*登录 -> 创建猫咪档案 -> 上传声音查情绪 -> 发起 AI 提问*）的自动化测试，在发布前强力拦截回归问题。