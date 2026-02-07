from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Integer

class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False)

class User(UserBase, table=True):
    """
    User model representing a registered user in the system.
    """
    id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    password_hash: str = Field(nullable=False)  # Store hashed passwords
    name: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversations
    conversations: List["Conversation"] = Relationship(back_populates="user")

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")


    # Add property to get user_id for JWT
    @property
    def user_id(self) -> int:
        return self.id

class UserCreate(UserBase):
    name: Optional[str] = None  # Make name optional for registration
    password: str

class UserRead(UserBase):
    id: int
    name: Optional[str]