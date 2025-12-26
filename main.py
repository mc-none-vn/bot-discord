from fastapi.responses import PlainTextResponse, JSONResponse, Response
from fastapi import FastAPI, Header, HTTPException, Path
import os, json


app = FastAPI()
API_KEY = os.getenv("API_KEY")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if not API_KEY:
    raise RuntimeError("API_KEY not set")


def verify_api_key(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/{file_path:path}")
async def get_static_file(file_path: str = Path(..., description="Path from project root"), x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    if ".." in file_path or file_path.startswith("/"):
        raise HTTPException(status_code=403, detail="Access denied")

    abs_path = os.path.abspath(os.path.join(ROOT_DIR, file_path))

    if not abs_path.startswith(ROOT_DIR):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.isfile(abs_path):
        raise HTTPException(status_code=404, detail="File not found")

    ext = os.path.splitext(abs_path)[1].lower()

    if ext == ".json":
        with open(abs_path, "r", encoding="utf-8") as f:
            return JSONResponse(json.load(f))

    if ext in {".txt", ".md", ".log"}:
        with open(abs_path, "r", encoding="utf-8") as f:
            return PlainTextResponse(f.read())

    with open(abs_path, "rb") as f:
        return Response(
            content=f.read(),
            media_type="application/octet-stream",
        )
