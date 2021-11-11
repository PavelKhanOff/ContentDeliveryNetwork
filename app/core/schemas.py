from pydantic import BaseModel
from typing import Optional


class DeleteScheme(BaseModel):
    cdn_key: str


class Avatar(BaseModel):
    achievement_id: Optional[int] = None
    course_id: Optional[int] = None
