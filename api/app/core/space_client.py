"""
Fallback client for tasks that have no working model on HF's free
`hf-inference` serverless provider, but do have a public Hugging Face Space
with a documented Gradio API. Spaces use a two-step protocol: POST to start
the job, then GET an SSE stream for the result. Image outputs come back as a
file reference (path/url) rather than inline bytes, so callers fetch it
separately via `fetch_space_file`.
"""

import base64
import json
import uuid
from typing import Callable, Optional

import requests

from app.core.config import HF_TOKEN


class SpaceInferenceError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def _auth_headers() -> dict:
    """Some Spaces run on ZeroGPU, which rate-limits anonymous callers hard —
    passing our HF token grants normal per-user quota instead."""
    return {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}


def _call_space_sse(space_host: str, api_name: str, data: list) -> list:
    """Shared SSE call/poll logic for Gradio's `/gradio_api/call/*` protocol."""
    start_url = f"https://{space_host}/gradio_api/call/{api_name}"
    start_resp = requests.post(start_url, json={"data": data}, headers=_auth_headers(), timeout=60)
    if start_resp.status_code >= 400:
        raise SpaceInferenceError(f"Space did not accept the request: {start_resp.text}")

    event_id = start_resp.json().get("event_id")
    if not event_id:
        raise SpaceInferenceError("Space did not return an event_id")

    result_url = f"{start_url}/{event_id}"
    with requests.get(result_url, headers=_auth_headers(), stream=True, timeout=120) as resp:
        event_type = None
        for raw_line in resp.iter_lines(decode_unicode=True):
            if raw_line is None or raw_line == "":
                continue
            if raw_line.startswith("event:"):
                event_type = raw_line.split(":", 1)[1].strip()
            elif raw_line.startswith("data:"):
                data_str = raw_line.split(":", 1)[1].strip()
                if event_type == "error":
                    raise SpaceInferenceError(f"Space returned an error: {data_str}")
                if event_type == "complete":
                    return json.loads(data_str)

    raise SpaceInferenceError("Space stream ended without a result")


def _call_space_with_image(space_host: str, api_name: str, image_bytes: bytes, extra_args: Optional[list] = None) -> list:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data = [{"url": f"data:image/jpeg;base64,{b64}", "meta": {"_type": "gradio.FileData"}}, *(extra_args or [])]
    return _call_space_sse(space_host, api_name, data)


def call_space_no_input(space_host: str, api_name: str, args: list) -> list:
    """For Spaces whose named API takes no image (e.g. unconditional generation)."""
    return _call_space_sse(space_host, api_name, args)


def query_space_text_output(space_host: str, api_name: str, image_bytes: bytes) -> str:
    """For Spaces whose named API returns a plain string (e.g. a caption)."""
    data = _call_space_with_image(space_host, api_name, image_bytes)
    return data[0] if data else ""


def query_space_multi_output(
    space_host: str, api_name: str, image_bytes: bytes, extra_args: list
) -> list:
    """For Spaces whose named API returns multiple outputs (e.g. an annotated
    image plus a raw JSON payload). Returns the raw parsed output list."""
    return _call_space_with_image(space_host, api_name, image_bytes, extra_args)


def call_classic_space(space_host: str, fn_index: int, data: list) -> list:
    """Older Gradio (v3) Spaces answer synchronously on /api/predict with no
    event-stream step, and typically return image outputs as inline base64
    data: URLs already."""
    url = f"https://{space_host}/api/predict"
    resp = requests.post(url, json={"data": data, "fn_index": fn_index}, timeout=90)
    if resp.status_code >= 400:
        raise SpaceInferenceError(f"Space did not accept the request: {resp.text}")
    body = resp.json()
    if "error" in body and body["error"]:
        raise SpaceInferenceError(f"Space returned an error: {body['error']}")
    return body.get("data", [])


def _join_and_poll_queue(space_host: str, fn_index: int, data: list) -> list:
    """Shared join/poll logic for Gradio's older `/queue/join` + `/queue/data`
    protocol, used by Spaces that enable queueing but predate the newer
    `/gradio_api/call/*` route. Each SSE line is a single self-contained JSON
    event (unlike the event:/data: pair format the newer route uses)."""
    session_hash = uuid.uuid4().hex

    join_url = f"https://{space_host}/queue/join"
    join_resp = requests.post(
        join_url,
        json={"data": data, "fn_index": fn_index, "session_hash": session_hash},
        headers=_auth_headers(),
        timeout=30,
    )
    if join_resp.status_code >= 400:
        raise SpaceInferenceError(f"Space did not accept the request: {join_resp.text}")

    stream_url = f"https://{space_host}/queue/data?session_hash={session_hash}"
    with requests.get(stream_url, headers=_auth_headers(), stream=True, timeout=180) as resp:
        for raw_line in resp.iter_lines(decode_unicode=True):
            if not raw_line or not raw_line.startswith("data:"):
                continue
            event = json.loads(raw_line[len("data:"):].strip())
            if event.get("msg") == "process_completed":
                output = event.get("output") or {}
                if not event.get("success"):
                    raise SpaceInferenceError(f"Space returned an error: {output.get('error')}")
                return output.get("data", [])

    raise SpaceInferenceError("Space stream ended without a result")


def call_queue_space(
    space_host: str,
    fn_index: int,
    image_bytes: bytes,
    build_data: Callable[[dict], list],
    orig_name: str = "image.jpg",
    content_type: str = "image/jpeg",
) -> list:
    """Newer Gradio (v4) Spaces with queueing enabled reject direct /api/predict
    calls and require: upload the file to get a server-side path, then join the
    queue and poll for the result.
    `build_data` receives the uploaded file's FileData dict and returns the full
    `data` array for the call (placing it wherever the target function expects)."""
    upload_url = f"https://{space_host}/upload"
    upload_resp = requests.post(
        upload_url,
        files={"files": (orig_name, image_bytes, content_type)},
        headers=_auth_headers(),
        timeout=60,
    )
    if upload_resp.status_code >= 400:
        raise SpaceInferenceError(f"Space rejected the file upload: {upload_resp.text}")
    paths = upload_resp.json()
    if not paths:
        raise SpaceInferenceError("Space upload did not return a file path")

    file_data = {
        "path": paths[0],
        "orig_name": orig_name,
        "mime_type": content_type,
        "meta": {"_type": "gradio.FileData"},
    }
    data = build_data(file_data)
    return _join_and_poll_queue(space_host, fn_index, data)


def call_queue_space_text(space_host: str, fn_index: int, data: list) -> list:
    """For queue-protocol Spaces whose function takes no file input (e.g. a
    pure text-to-video prompt)."""
    return _join_and_poll_queue(space_host, fn_index, data)


def fetch_file_as_data_url(file_url: str) -> str:
    file_resp = requests.get(file_url, headers=_auth_headers(), timeout=60)
    if file_resp.status_code >= 400:
        raise SpaceInferenceError(f"Could not download the Space's output file: {file_resp.status_code}")
    content_type = file_resp.headers.get("content-type", "image/webp")
    encoded = base64.b64encode(file_resp.content).decode("utf-8")
    return f"data:{content_type};base64,{encoded}"


def query_space_image_output(
    space_host: str,
    api_name: str,
    image_bytes: bytes,
    extra_args: Optional[list] = None,
    output_index: int = 0,
) -> str:
    """For Spaces whose named API returns an image file among its outputs.
    Returns a base64 data: URL."""
    data = _call_space_with_image(space_host, api_name, image_bytes, extra_args)
    if not data or len(data) <= output_index or not isinstance(data[output_index], dict) or "url" not in data[output_index]:
        raise SpaceInferenceError("Space did not return an image file reference")
    return fetch_file_as_data_url(data[output_index]["url"])
