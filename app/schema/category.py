from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    description: str | None = None

class CategoryCreate(CategoryBase):
    """Schema for creating a new category.
    """
    pass

class CategoryUpdate(CategoryBase):
    """Schema for updating an existing category.
    """
    name: str | None = None
    description: str | None = None

class CategoryInDBBase(CategoryBase):
    """Schema for representing a category in the database.
    """
    id: int

    class Config:
        from_attributes  = True

class Category(CategoryInDBBase):
    """Schema return for clinet"""
    pass
