from pydantic import BaseModel, EmailStr


class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: str

    class Config:
        from_attributes = True



class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True