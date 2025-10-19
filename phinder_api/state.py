from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel

from phinder_api.models.vt_analysis import Attributes


class FileRecord(BaseModel):
    size: str
    uploaded_at: datetime
    analysis_id: str
    analysis_status: str  # queued, in-progress, completed, etc.


class InMemoryStore:
    _instance = None
    files_loaded: Dict[str, FileRecord]
    analysis_results: Dict[str, Attributes]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.files_loaded = {}
            cls._instance.analysis_results = {}
        return cls._instance

    # === FILES LOADED ===
    def add_file(self, sha256: str, size: str, vt_id: str):
        self.files_loaded[sha256] = FileRecord(
            size=size,
            uploaded_at=datetime.now(timezone.utc),
            analysis_id=vt_id,
            analysis_status="queued",
        )

    def update_file_status(self, sha256: str, status: str):
        if sha256 in self.files_loaded:
            record = self.files_loaded[sha256]
            updated = record.model_copy(update={"analysis_status": status})
            self.files_loaded[sha256] = updated

    def get_file(self, sha256: str) -> Optional[FileRecord]:
        return self.files_loaded.get(sha256)

    # === ANALYSIS RESULTS ===
    def upsert_analysis_result(self, vt_id: str, attributes: Attributes):
        self.analysis_results[vt_id] = attributes

    def get_analysis_result(self, vt_id: str) -> Optional[Attributes]:
        return self.analysis_results.get(vt_id)
