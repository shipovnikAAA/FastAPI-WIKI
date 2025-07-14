from pydantic import BaseModel, Field
from typing import Annotated
from pydantic.functional_validators import AfterValidator
from main.core.errors import ValidationErrorHandler
from fastapi import Query
import re
    
class PUTTitle(BaseModel):
    title: str = Query(
        description="Title of the wiki",
    )
    parent: float = Query(
        description="parent of the title",
    )

class GETTitlesParent(BaseModel):
    title: str = Field(Query(
        description="Titlte for get parents",
    ))
    
class Paginated(BaseModel):
    page: int = Field(Query(
        description='count of page',
        example="1",
        ge=1
    ))
    per_page: int = Field(Query(
        description="items in page",
        example="10",
        ge=1
    ))
    sort_by: str | None = Field(Query(
        description="Column name to sort by",
        example="time",
        default=None
    ))
    sort_order: str | None = Field(Query(
        description="Sort order (asc or desc)",
        example="desc",
        pattern="^(asc|desc)$",
        default=None
    ))
    
class ReturnALLS(BaseModel):
    pagination: Paginated
    data: list[dict | None]
    total: int | None
    total_pages: int