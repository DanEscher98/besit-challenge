from typing import Dict, Optional
from pydantic import BaseModel, Field


class EngineResult(BaseModel):
    category: Optional[str]
    engine_name: Optional[str]
    engine_version: Optional[str]
    engine_update: Optional[str]
    method: Optional[str]
    result: Optional[str]


class Stats(BaseModel):
    confirmed_timeout: Optional[int] = Field(None, alias="confirmed-timeout")
    failure: Optional[int]
    harmless: Optional[int]
    malicious: Optional[int]
    suspicious: Optional[int]
    timeout: Optional[int]
    type_unsupported: Optional[int] = Field(None, alias="type-unsupported")
    undetected: Optional[int]


class Attributes(BaseModel):
    date: int
    results: Dict[str, EngineResult] = {}
    stats: Stats
    status: str


class AnalysisData(BaseModel):
    id: str
    type: str = "analysis"
    links: Dict[str, str] = {}
    attributes: Attributes


class FileInfo(BaseModel):
    sha256: str
    md5: str
    sha1: str
    size: int


class AnalysisMetadata(BaseModel):
    file_info: FileInfo


class AnalysisResponse(BaseModel):
    """
    Top-level response model for VirusTotal Analyses.
    Use AnalysisResponse.parse_obj(response.json()) to convert a JSON dict
    """

    data: AnalysisData
    meta: AnalysisMetadata
