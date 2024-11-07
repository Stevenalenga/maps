from pydantic import BaseModel, EmailStr


class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True



class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True