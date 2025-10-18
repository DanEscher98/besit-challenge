from fastapi import UploadFile
from typing import Optional
import httpx

from phinder_api.models.vt_analysis import AnalysisResponse
from phinder_api import VT_APIKEY, VT_APIURL
from phinder_api.state import InMemoryStore

import asyncio


async def track_analysis_updates(store: InMemoryStore):
    while True:
        for sha256, record in list(store.files_loaded.items()):
            vt_id = record.analysis_id
            analysis = await get_analysis_from_virustotal(vt_id)
            status = analysis.data.attributes.status

            store.update_file_status(sha256, status)

            if not (status == "queued"):
                store.upsert_analysis_result(vt_id, analysis.data.attributes)

        await asyncio.sleep(15)


async def upload_file_to_virustotal(file: UploadFile) -> str:
    contents: bytes = await file.read()
    await file.close()

    if not contents:
        raise RuntimeError("Uploaded file is empty")

    # (filename, bytes, content_type)
    file_tuple = (
        file.filename or "upload",
        contents,
        file.content_type or "application/octet-stream",
    )

    headers = {"x-apikey": VT_APIKEY}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{VT_APIURL}/files", headers=headers, files={"file": file_tuple}
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"VirusTotal upload failed: {exc.response.status_code} - {exc.response.text}"
        ) from exc

    payload = response.json()
    vt_id: Optional[str] = payload.get("data", {}).get("id")

    if not vt_id:
        raise RuntimeError(f"VirusTotal response missing data.id: {payload!r}")

    return vt_id


async def get_analysis_from_virustotal(vt_id: str) -> AnalysisResponse:
    headers = {"x-apikey": VT_APIKEY}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(f"{VT_APIURL}/analyses/{vt_id}", headers=headers)

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"VirusTotal analysis failed: {exc.response.status_code} - {exc.response.text}"
        ) from exc

    analysis = AnalysisResponse.parse_obj(response.json())

    return analysis
