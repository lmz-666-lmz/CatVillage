# 猫咪主题社交与健康管理 APP 接口文档

## 项目概述

这是一个跨端猫咪主题社交与健康管理 APP，前端使用 Vue3 技术栈，后端使用 Python 开发，采用前后端分离架构。所有接口均遵循 RESTful 规范，返回统一的数据格式。

## 接口规范

### 通用规范
- **协议**：HTTPS
- **字符编码**：UTF-8
- **返回格式**：JSON
- **统一返回格式**：
```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

### 状态码定义
- 200：请求成功
- 400：参数错误
- 401：未授权
- 403：无权限
- 404：资源不存在
- 500：服务器内部错误

### 鉴权规范
- 个人业务相关接口必须携带 `Authorization: Bearer {token}` 请求头
- 公开浏览类接口无需鉴权

---

## 前端（Vue3）接口调用规范

### 1. 网络请求封装

```javascript
// utils/request.js
import axios from 'axios';

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
});

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

request.interceptors.response.use(
  response => {
    const res = response.data;
    if (res.code !== 200) {
      console.error(res.msg);
      return Promise.reject(new Error(res.msg || 'Error'));
    } else {
      return res;
    }
  },
  error => {
    console.error(error);
    return Promise.reject(error);
  }
);

export default request;
```

### 2. 接口服务层

#### 宠物数字档案管理服务
```javascript
// api/petProfile.js
import request from '@/utils/request';

// 新增猫咪档案
export function createCatProfile(data) {
  return request({
    url: '/pet-profiles',
    method: 'post',
    data
  });
}

// 编辑猫咪档案
export function updateCatProfile(catId, data) {
  return request({
    url: `/pet-profiles/${catId}`,
    method: 'put',
    data
  });
}

// 查询猫咪档案详情
export function getCatProfile(catId) {
  return request({
    url: `/pet-profiles/${catId}`,
    method: 'get'
  });
}

// 删除猫咪档案
export function deleteCatProfile(catId) {
  return request({
    url: `/pet-profiles/${catId}`,
    method: 'delete'
  });
}

// 查询用户猫咪列表
export function getCatList(params) {
  return request({
    url: '/pet-profiles/list',
    method: 'get',
    params
  });
}
```

#### 交友广场服务
```javascript
// api/social.js
import request from '@/utils/request';

// 发布动态
export function publishDynamic(data) {
  return request({
    url: '/social/dynamics',
    method: 'post',
    headers: { 'Content-Type': 'multipart/form-data' },
    data
  });
}

// 获取广场动态列表
export function getDynamicsList(params) {
  return request({
    url: '/social/dynamics/list',
    method: 'get',
    params
  });
}

// 获取动态详情
export function getDynamicDetail(dynamicId) {
  return request({
    url: `/social/dynamics/${dynamicId}`,
    method: 'get'
  });
}

// 点赞动态
export function likeDynamic(dynamicId) {
  return request({
    url: `/social/dynamics/${dynamicId}/like`,
    method: 'post'
  });
}

// 取消点赞
export function unlikeDynamic(dynamicId) {
  return request({
    url: `/social/dynamics/${dynamicId}/like`,
    method: 'delete'
  });
}

// 发表评论
export function postComment(dynamicId, data) {
  return request({
    url: `/social/dynamics/${dynamicId}/comments`,
    method: 'post',
    data
  });
}

// 删除评论
export function deleteComment(commentId) {
  return request({
    url: `/social/comments/${commentId}`,
    method: 'delete'
  });
}

// 删除动态
export function deleteDynamic(dynamicId) {
  return request({
    url: `/social/dynamics/${dynamicId}`,
    method: 'delete'
  });
}

// 获取我的动态列表
export function getMyDynamicsList(params) {
  return request({
    url: '/social/dynamics/my/list',
    method: 'get',
    params
  });
}
```

#### 好友消息服务
```javascript
// api/message.js
import request from '@/utils/request';

// 获取好友列表
export function getFriendList(params) {
  return request({
    url: '/friends/list',
    method: 'get',
    params
  });
}

// 发送消息
export function sendMessage(data) {
  return request({
    url: '/messages/send',
    method: 'post',
    data
  });
}

// 撤回消息
export function revokeMessage(messageId) {
  return request({
    url: `/messages/${messageId}/revoke`,
    method: 'put'
  });
}

// 更新消息已读状态
export function updateReadStatus(messageIds) {
  return request({
    url: '/messages/read-status',
    method: 'put',
    data: { messageIds }
  });
}

// 发送快捷喵语
export function sendQuickMeow(receiverId, meowType) {
  return request({
    url: '/messages/quick-meow',
    method: 'post',
    data: { receiverId, meowType }
  });
}

// 获取会话列表
export function getConversationList(params) {
  return request({
    url: '/conversations/list',
    method: 'get',
    params
  });
}

// 获取会话历史消息
export function getConversationMessages(targetUserId, params) {
  return request({
    url: `/conversations/${targetUserId}/messages`,
    method: 'get',
    params
  });
}

// 删除会话
export function deleteConversation(targetUserId) {
  return request({
    url: `/conversations/${targetUserId}`,
    method: 'delete'
  });
}
```

#### 喵喵情绪台服务
```javascript
// api/emotion.js
import request from '@/utils/request';

// 上传音频并识别情绪
export function recognizeEmotion(data) {
  return request({
    url: '/emotion/recognize',
    method: 'post',
    headers: { 'Content-Type': 'multipart/form-data' },
    data
  });
}

// 获取情绪识别历史记录
export function getEmotionRecords(params) {
  return request({
    url: '/emotion/records/list',
    method: 'get',
    params
  });
}

// 获取单条情绪记录详情
export function getEmotionRecordDetail(recordId) {
  return request({
    url: `/emotion/records/${recordId}`,
    method: 'get'
  });
}

// 获取情绪统计可视化数据
export function getEmotionStatistics(params) {
  return request({
    url: '/emotion/statistics',
    method: 'get',
    params
  });
}

// 获取健康预警列表
export function getWarningList(params) {
  return request({
    url: '/emotion/warnings/list',
    method: 'get',
    params
  });
}

// 标记预警状态
export function markWarningStatus(warningId, status) {
  return request({
    url: `/emotion/warnings/${warningId}/status`,
    method: 'put',
    data: { status }
  });
}

// 生成情绪周报
export function getWeeklyReport(params) {
  return request({
    url: '/emotion/weekly-report',
    method: 'get',
    params
  });
}
```

#### AI 养育助理服务
```javascript
// api/aiAssistant.js
import request from '@/utils/request';

// 发起对话提问
export function chatWithAI(data) {
  return request({
    url: '/ai-assistant/chat',
    method: 'post',
    data
  });
}

// 获取对话历史
export function getChatHistory(params) {
  return request({
    url: '/ai-assistant/history',
    method: 'get',
    params
  });
}

// 结束/清空会话
export function clearSession(sessionId) {
  return request({
    url: `/ai-assistant/sessions/${sessionId}`,
    method: 'delete'
  });
}

// 一键求助（通过健康预警）
export function emergencyHelp(warningId, data) {
  return request({
    url: `/ai-assistant/emergency-help/${warningId}`,
    method: 'post',
    data
  });
}
```

---

## 后端（Python）接口实现规范

### 1. 项目结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── cat_profile.py
│   │   ├── social.py
│   │   ├── message.py
│   │   ├── emotion.py
│   │   └── ai_assistant.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── cat_profile.py
│   │   ├── social.py
│   │   ├── message.py
│   │   ├── emotion.py
│   │   └── ai_assistant.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── pet_profiles.py
│   │   │   ├── social.py
│   │   │   ├── messages.py
│   │   │   ├── emotions.py
│   │   │   └── ai_assistant.py
│   │   └── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py
│   └── core/
│       ├── __init__.py
│       ├── config.py
│       ├── security.py
│       └── dependencies.py
├── requirements.txt
├── alembic.ini
└── main.py
```

### 2. 核心依赖包
```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
minio==7.2.3
numpy==1.26.2
torch==2.1.1
transformers==4.35.2
openai==1.3.5
```

### 3. 数据模型定义示例

```python
# models/cat_profile.py
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CatProfile(Base):
    __tablename__ = "cat_profiles"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    breed = Column(String, nullable=False)
    age = Column(Integer, nullable=False)  # 月龄
    gender = Column(Integer, nullable=False)  # 0-母，1-公
    weight = Column(Float)
    is_neutered = Column(Boolean, default=False)
    medical_history = Column(String)
    vaccine_status = Column(String)
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 4. API 实现示例

```python
# api/v1/pet_profiles.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, database
from ..core.security import get_current_user
from ..database.session import get_db

router = APIRouter(prefix="/pet-profiles", tags=["pet-profiles"])

@router.post("/", response_model=schemas.CatProfileResponse)
def create_cat_profile(
    profile: schemas.CatProfileCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建猫咪档案"""
    import uuid
    from datetime import datetime
    
    db_profile = models.CatProfile(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=profile.name,
        breed=profile.breed,
        age=profile.age,
        gender=profile.gender,
        weight=profile.weight,
        is_neutered=profile.is_neutered,
        medical_history=profile.medical_history,
        vaccine_status=profile.vaccine_status,
        created_at=datetime.utcnow()
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile


@router.get("/{cat_id}", response_model=schemas.CatProfileResponse)
def get_cat_profile(
    cat_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取猫咪档案详情"""
    profile = db.query(models.CatProfile).filter(
        models.CatProfile.id == cat_id,
        models.CatProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="猫咪档案不存在"
        )
    
    return profile


@router.put("/{cat_id}", response_model=schemas.CatProfileResponse)
def update_cat_profile(
    cat_id: str,
    profile_update: schemas.CatProfileUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新猫咪档案"""
    profile = db.query(models.CatProfile).filter(
        models.CatProfile.id == cat_id,
        models.CatProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="猫咪档案不存在"
        )
    
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    
    return profile


@router.delete("/{cat_id}")
def delete_cat_profile(
    cat_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除猫咪档案"""
    profile = db.query(models.CatProfile).filter(
        models.CatProfile.id == cat_id,
        models.CatProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="猫咪档案不存在"
        )
    
    db.delete(profile)
    db.commit()
    
    return {"code": 200, "msg": "删除成功", "data": None}


@router.get("/list", response_model=schemas.CatProfileListResponse)
def get_cat_list(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取用户猫咪列表"""
    profiles = db.query(models.CatProfile).filter(
        models.CatProfile.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    total = db.query(models.CatProfile).filter(
        models.CatProfile.user_id == current_user.id
    ).count()
    
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "total": total,
            "list": profiles
        }
    }
```

### 5. 情绪识别模型集成

```python
# core/emotion_classifier.py
import torch
import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2Model
import librosa

class EmotionClassifier:
    def __init__(self, model_path):
        self.processor = Wav2Vec2Processor.from_pretrained(model_path)
        self.model = Wav2Vec2Model.from_pretrained(model_path)
        self.emotion_labels = ['开心', '舒适', '疼痛警告', '焦虑', '应激', '饥饿']
        
    def predict(self, audio_path):
        # 加载音频文件
        speech_array, sampling_rate = librosa.load(audio_path, sr=16000)
        
        # 预处理
        inputs = self.processor(
            speech_array, 
            sampling_rate=16000, 
            return_tensors="pt", 
            padding=True
        )
        
        # 特征提取
        with torch.no_grad():
            outputs = self.model(**inputs)
            hidden_states = outputs.last_hidden_state.mean(dim=1)
            
        # 情绪分类（这里简化，实际应用中需要训练分类器）
        # 返回预测的情绪标签和置信度
        probabilities = torch.softmax(torch.randn(1, len(self.emotion_labels)), dim=1)
        predicted_idx = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][predicted_idx].item()
        
        return {
            "emotion_tag": self.emotion_labels[predicted_idx],
            "confidence": confidence,
            "emotion_description": f"系统检测到猫咪处于{self.emotion_labels[predicted_idx]}状态"
        }
```

### 6. 主应用入口

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import (
    pet_profiles, 
    social, 
    messages, 
    emotions, 
    ai_assistant
)

app = FastAPI(title="猫咪社交与健康管理后端", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请具体设置
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(pet_profiles.router, prefix="/api/v1", tags=["pet-profiles"])
app.include_router(social.router, prefix="/api/v1", tags=["social"])
app.include_router(messages.router, prefix="/api/v1", tags=["messages"])
app.include_router(emotions.router, prefix="/api/v1", tags=["emotions"])
app.include_router(ai_assistant.router, prefix="/api/v1", tags=["ai-assistant"])

@app.get("/")
def read_root():
    return {"Hello": "Welcome to Cat Social & Health Management API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 7. 启动命令

```bash
# 开发环境启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产环境启动
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 部署指南

### 前端部署
1. 构建生产版本：`npm run build`
2. 将 dist 目录部署到 CDN 或 Nginx 服务器

### 后端部署
1. 配置环境变量：数据库连接、Redis 连接、存储配置等
2. 执行数据库迁移：`alembic upgrade head`
3. 启动应用：使用 Gunicorn 或 Uvicorn

---

## 注意事项

1. 所有猫咪相关的业务操作必须以 `catId` 为核心关联参数
2. 用户切换当前选中的猫咪档案时，四大业务模块的数据需自动切换至对应 [catId](file:///C:/Users/%E9%AB%98%E9%B9%8F%E6%96%90/Desktop/%E6%8E%A5%E5%8F%A3.md#L26-L26) 的专属数据
3. 媒体文件（图片、音频）需存储到对象存储服务
4. 情绪识别需调用自研模型，确保准确性和响应速度
5. AI 助理需整合猫咪档案、情绪数据和用户提问构建 Prompt