from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    pet_id: str
    user_message: str


class ChatHistoryResponse(BaseModel):
    id: int
    pet_id: str
    question: str
    answer: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)