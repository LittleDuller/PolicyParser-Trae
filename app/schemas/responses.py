from pydantic import BaseModel, Field


class ClassificationResponse(BaseModel):
    category: str = Field(description="政策主要影响的行业分类")
    confidence: float = Field(description="分类置信度，0.0-1.0之间")
