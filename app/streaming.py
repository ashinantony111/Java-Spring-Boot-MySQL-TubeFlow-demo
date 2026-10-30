import os
from pathlib import Path
from typing import Generator
from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse

CHUNK_SIZE = 1024 * 1024  # 1MB chunk

def range_stream_generator(file_path: Path, start: int, end: int) -> Generator[bytes, None, None]:
    with open(file_path, "rb") as f:
        f.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            chunk_bytes = min(CHUNK_SIZE, remaining)
            data = f.read(chunk_bytes)
            if not data:
                break
            remaining -= len(data)
            yield data

def stream_video_file(file_path: Path, request: Request):
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    file_size = file_path.stat().st_size
    range_header = request.headers.get("range")

    if not range_header:
        # Full content response
        return FileResponse(file_path, media_type="video/mp4")

    # Range: bytes=start-end
    range_val = range_header.replace("bytes=", "").strip()
    parts = range_val.split("-")
    start = int(parts[0]) if parts[0] else 0
    end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1

    if start >= file_size or end >= file_size or start > end:
        raise HTTPException(status_code=416, detail="Requested Range Not Satisfiable")

    content_length = end - start + 1
    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Content-Type": "video/mp4",
    }

    return StreamingResponse(
        range_stream_generator(file_path, start, end),
        status_code=206,
        headers=headers
    )
