from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=16)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=16)


class CategoryOut(CategoryBase):
    id: int
    slug: str
    organization_id: int | None

    model_config = {"from_attributes": True}


class CategorySummary(BaseModel):
    id: int
    name: str
    slug: str
    organization_id: int | None

    model_config = {"from_attributes": True}
