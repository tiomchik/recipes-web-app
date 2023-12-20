from pydantic import BaseModel, Field
from datetime import datetime


class RecipeCreate(BaseModel):
    headling: str = Field(min_length=10, max_length=50)
    text: str = Field(min_length=10)


class RecipeResponse(BaseModel):
    id: int
    headling: str
    text: str
    pub_date: datetime
    author: str
