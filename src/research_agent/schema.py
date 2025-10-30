from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    page: Optional[int] = Field(default=None, description="Page number if known")
    text: str = Field(description="Quoted or paraphrased snippet")


class Section(BaseModel):
    title: str
    bullets: List[str] = Field(default_factory=list)


class Report(BaseModel):
    doc_title: str
    doc_meta: dict = Field(default_factory=dict)
    key_findings: Section
    methodology: Section
    limitations: Section
    important_quotes: List[Citation] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    pages_covered: Optional[int] = None
