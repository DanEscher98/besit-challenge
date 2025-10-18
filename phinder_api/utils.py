import hashlib
from fastapi import UploadFile


def format_size(num_bytes: int) -> str:
    units = ["bytes", "KB", "MB", "GB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == "GB":
            return f"{size:.2f} {unit}"
        size /= 1024


async def compute_sha256(upload_file: UploadFile) -> str:
    hash_obj = hashlib.sha256()
    while chunk := await upload_file.read(4096):
        hash_obj.update(chunk)
    await upload_file.seek(0)
    return hash_obj.hexdigest()
