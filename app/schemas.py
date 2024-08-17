from pydantic import BaseModel


#--------------------------------------------------------

class TaksDB(BaseModel):
    id: int
    title: str
    description: str | None = None
    owner_id: int

    class Config:
        orm_mode = True

#--------------------------------------------------------
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None

#--------------------------------------------------------


class UserDB(BaseModel):
    id: int
    username: str
    email: str | None = None
    is_active: bool | None = None

    class Config:
        orm_mode = True

class UserTasks(UserDB):
    tasks: list[TaksDB] = []

    class Config:
        orm_mode = True


class UserInDB(UserDB):
    hashed_password: str

#--------------------------------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None
    username: str | None = None
