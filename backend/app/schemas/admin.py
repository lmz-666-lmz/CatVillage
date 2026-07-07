from pydantic import BaseModel


class AdminTogglePayload(BaseModel):
    value: bool


class AdminConfigPayload(BaseModel):
    aiApiKey: str | None = None
    aiBaseUrl: str | None = None
    aiModel: str | None = None


class AdminPasswordPayload(BaseModel):
    password: str


class AdminTopicsPayload(BaseModel):
    topics: list[str]


class AdminStats(BaseModel):
    users: int
    pets: int
    dynamics: int
    emotion_records: int
    today_users: int = 0
    today_dynamics: int = 0
    messages: int
    health_records: int = 0
    ai_chats: int = 0
    active_users: int = 0
    disabled_users: int = 0
    admins: int = 0


class AdminListResponse(BaseModel):
    list: list[dict]
    total: int
    page: int
    pageSize: int
