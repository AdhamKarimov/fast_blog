from pydantic import BaseModel
from typing import Optional


class SignUp(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    username: str
    email: str
    password: str


class Login(BaseModel):
    username: str
    password: str


class Settings(BaseModel):
    authjwt_secret_key: str="9db9dd2b4e07c24272d2d4f84ca8238d1949b53e191786483f4c806d3b13d4c6"



class Updateprofil(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True


class PasswordResert(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str
    class Config:
        from_attributes = True