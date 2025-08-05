"""Search schemas for API request/response validation."""
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class DateRangeSchema(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    type: str = Field(default="created", pattern="^(created|updated)$")

    @field_validator("end")
    @classmethod
    def validate_date_range(cls, v, info=None):  # type: ignore
        if v and info and hasattr(info, 'data') and info.data.get("start"):
            if v < info.data["start"]:
                raise ValueError("End date must be after start date")
        return v


class SearchFiltersSchema(BaseModel):
    tags: List[str] = Field(default_factory=list)
    authors: List[str] = Field(default_factory=list)
    date_range: Optional[DateRangeSchema] = None
    sort_by: str = Field(default="updated_at", pattern="^(created_at|updated_at|title)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tags": ["tag-id-1", "tag-id-2"],
                "authors": ["user-id-1", "user-id-2"],
                "date_range": {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-12-31T23:59:59Z",
                    "type": "created"
                },
                "sort_by": "updated_at",
                "sort_order": "desc"
            }
        }
    }


class TagSchema(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
    usage_count: Optional[int] = None

    model_config = {"from_attributes": True}


class UserSummarySchema(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None

    model_config = {"from_attributes": True}


class WhiteboardSearchResultSchema(BaseModel):
    id: str
    title: str
    description: str
    creator: UserSummarySchema
    tags: List[TagSchema]
    created_at: datetime
    updated_at: datetime
    is_public: bool
    collaborator_count: int

    model_config = {"from_attributes": True}


class SearchResponseSchema(BaseModel):
    results: List[WhiteboardSearchResultSchema]
    total: int
    page: int
    page_size: int
    has_next: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "results": [
                    {
                        "id": "whiteboard-id",
                        "title": "Project Planning",
                        "description": "Q1 2024 project planning board",
                        "creator": {
                            "id": "user-id",
                            "name": "John Doe",
                            "avatar": "https://example.com/avatar.jpg"
                        },
                        "tags": [
                            {
                                "id": "tag-id",
                                "name": "Planning",
                                "color": "#3B82F6"
                            }
                        ],
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-20T15:45:00Z",
                        "is_public": False,
                        "collaborator_count": 5
                    }
                ],
                "total": 42,
                "page": 1,
                "page_size": 10,
                "has_next": True
            }
        }
    }


class ValidationResult(BaseModel):
    is_valid: bool
    errors: Dict[str, List[str]] = Field(default_factory=dict)