from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime



class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    is_liked = Column(Boolean, default=False)
    user = relationship("User", back_populates="like")
    posts = relationship("Post", back_populates="like")
    created_at = Column(DateTime, default=datetime.now)
