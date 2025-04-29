from typing import List, Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    is_admin: Optional[bool] = False
    devices: Optional[List[int]] = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int


class UserModify(UserBase):
    username: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    devices: Optional[List[int]] = None
