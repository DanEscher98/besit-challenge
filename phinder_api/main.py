import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from phinder_api import utils, vt_utils
from phinder_api.models.response import APIResponse
from phinder_api.state import InMemoryStore
from phinder_api.vt_utils import track_analysis_updates

app = FastAPI()


@asynccontextmanager
async def lifespan(_: FastAPI):
    state = InMemoryStore()
    asyncio.create_task(track_analysis_updates(state))

    yield  # Control goes to the app


app.router.lifespan_context = lifespan


@app.exception_handler(HTTPException)
async def http_error_handler(_: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.fail(exc.detail, exc.status_code).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422, content=APIResponse.fail("Validation error", 422).model_dump()
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(_: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse.fail(
            str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
        ).model_dump(),
    )


@app.get("/", summary="Root API status endpoint")
def home():
    return {
        "message": "Phinder challenge API",
        "version": "0.0.1",
        "timestamp": datetime.now().isoformat(),
    }


@app.post(
    "/update",
    summary="Upload a file and trigger analysis",
    response_model=APIResponse[dict],
)
async def update(file: UploadFile = File(...)):
    state = InMemoryStore()
    sha256 = await utils.compute_sha256(file)
    cached = state.get_file(sha256)

    if cached:
        return APIResponse.ok({"vt_id": cached.analysis_id, "cached": True})

    vt_id = await vt_utils.upload_file_to_virustotal(file)
    size_str = utils.format_size(file.size if file.size else 0)
    state.add_file(sha256=sha256, size=size_str, vt_id=vt_id)

    return APIResponse.ok({"vt_id": vt_id, "cached": False})


@app.get(
    "/list_files", summary="List all uploaded files", response_model=APIResponse[dict]
)
async def list_files():
    state = InMemoryStore()
    return APIResponse.ok(
        {file: metadata for file, metadata in state.files_loaded.items()}
    )


@app.get(
    "/analysis/{vt_id}",
    summary="Get analysis result by VirusTotal ID",
    response_model=APIResponse[dict],
)
async def analysis(vt_id: str):
    state = InMemoryStore()
    data = state.analysis_results.get(vt_id)

    if not data:
        payload = APIResponse.fail(
            f"Analysis not found for vt_id={vt_id}", status.HTTP_404_NOT_FOUND
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content=payload.model_dump()
        )

    return APIResponse.ok(data.model_dump())
