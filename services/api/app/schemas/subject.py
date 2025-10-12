from pydantic import BaseModel, Field


class SubjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=16)


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=16)


class SubjectOut(SubjectBase):
    id: int
    slug: str
    organization_id: int | None

    model_config = {"from_attributes": True}


class SubjectSummary(BaseModel):
    id: int
    name: str
    slug: str
    organization_id: int | None

    model_config = {"from_attributes": True}
