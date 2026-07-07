"""
专业医生模块 — 模拟实现

本页面内容仅为模拟展示，不构成真实兽医诊断或医疗建议。
如有宠物健康问题，请及时联系线下正规宠物医院。
"""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/doctors", tags=["doctors"])

MOCK_DOCTORS = [
    {
        "id": "d-1",
        "name": "张医生",
        "title": "高级兽医师 · 12年经验",
        "tags": ["全科", "猫科行为学"],
        "price": 49,
        "rating": "4.9",
        "online": False,
        "avatar": "",
        "is_mock": True,
        "status_text": "模拟数据",
    },
    {
        "id": "d-2",
        "name": "李医生",
        "title": "副主任兽医师 · 外科专家",
        "tags": ["骨科", "软组织外科"],
        "price": 88,
        "rating": "5.0",
        "online": False,
        "avatar": "",
        "is_mock": True,
        "status_text": "模拟数据",
    },
    {
        "id": "d-3",
        "name": "王医生",
        "title": "特聘宠物心理学专家",
        "tags": ["情绪抚慰", "应激处理"],
        "price": 60,
        "rating": "4.8",
        "online": False,
        "avatar": "",
        "is_mock": True,
        "status_text": "模拟数据",
    },
]


@router.get("/list")
def list_doctors(
    keyword: str | None = Query(None),
    current_user: User = Depends(get_current_user),
):
    """获取推荐医生列表（模拟数据）"""
    doctors = MOCK_DOCTORS
    if keyword:
        keyword_lower = keyword.strip().lower()
        doctors = [
            d for d in doctors
            if keyword_lower in d["name"].lower()
            or keyword_lower in d["title"].lower()
            or any(keyword_lower in tag.lower() for tag in d["tags"])
        ]
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "list": doctors,
            "total": len(doctors),
            "is_mock": True,
            "mock_notice": "当前为模拟数据，功能待完善。本页面内容仅为模拟展示，不构成真实兽医诊断或医疗建议。",
        },
    }


@router.get("/tips")
def get_consult_tips():
    """获取咨询小贴士（无需认证）"""
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "tips": [
                {
                    "title": "提前准备宠物基本信息",
                    "content": "包括年龄、体重、疫苗情况及既往病史。",
                },
                {
                    "title": "多角度拍摄患处",
                    "content": "清晰照片能帮助医生更准确判断病情。",
                },
            ],
            "is_mock": True,
            "mock_notice": "当前为模拟数据，功能待完善。本页面内容仅为模拟展示，不构成真实兽医诊断或医疗建议。",
        },
    }
