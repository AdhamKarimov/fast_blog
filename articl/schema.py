from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class PostCreate(BaseModel):
    title: str
    content: str
    image: Optional[str] = None

    @field_validator("title")
    def title_validator(cls, v):
        if len(v) < 3:
            raise ValueError("Title kamida 3 ta belgidan iborat bo'lishi kerak")
        if len(v) > 255:
            raise ValueError("Title 255 ta belgidan oshmasligi kerak")
        return v

    @field_validator("content")
    def content_validator(cls, v):
        if len(v) < 10:
            raise ValueError("Content kamida 10 ta belgidan iborat bo'lishi kerak")
        return v


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None

    @field_validator("title")
    def title_validator(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError("Title kamida 3 ta belgidan iborat bo'lishi kerak")
            if len(v) > 255:
                raise ValueError("Title 255 ta belgidan oshmasligi kerak")
        return v


class PostAuthor(BaseModel):
    username: str
    first_name: str

    model_config = {"from_attributes": True}


class PostDetail(BaseModel):
    id: int
    title: str
    content: str
    image: Optional[str] = None
    view_count: int
    created_at: datetime
    updated_at: datetime
    author: PostAuthor

    model_config = {"from_attributes": True}



class PostListResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    author:PostAuthor

