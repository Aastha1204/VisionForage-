"""
Thin, task-agnostic wrapper around the Hugging Face serverless Inference API.

Rather than hard-coding a Python method per task (which the `huggingface_hub`
SDK does inconsistently across tasks), we talk to the raw REST endpoint and
branch on the response's Content-Type — this makes it trivial to plug in any
of the 19 task categories with one shared code path.
"""

import base64
import json

import requests

from app.core.config import HF_INFERENCE_BASE, HF_TOKEN


class HFInferenceError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def _headers(extra: dict | None = None) -> dict:
    headers = {}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    if extra:
        headers.update(extra)
    return headers


def query_binary(
    model_id: str,
    binary_data: bytes,
    content_type: str = "application/octet-stream",
    params: dict | None = None,
) -> dict:
    """Send raw bytes (image/video) to a model, optionally with extra JSON params
    packed into the X-Wait-For-Model / query string per HF conventions."""
    url = f"{HF_INFERENCE_BASE}/{model_id}"
    headers = _headers({"X-Wait-For-Model": "true", "Content-Type": content_type})
    resp = requests.post(url, headers=headers, data=binary_data, params=params, timeout=120)
    return _parse_response(resp)


def query_json(model_id: str, payload: dict) -> dict:
    url = f"{HF_INFERENCE_BASE}/{model_id}"
    headers = _headers({"Content-Type": "application/json", "X-Wait-For-Model": "true"})
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
    return _parse_response(resp)


def query_image_with_text(model_id: str, image_bytes: bytes, prompt_fields: dict) -> dict:
    """For tasks like image-to-image / zero-shot classification that need both
    an image and extra text parameters, HF expects a JSON body with a base64
    image plus the extra fields."""
    payload = {
        "inputs": base64.b64encode(image_bytes).decode("utf-8"),
        **prompt_fields,
    }
    return query_json(model_id, payload)


def _parse_response(resp: requests.Response) -> dict:
    content_type = resp.headers.get("content-type", "")

    if resp.status_code >= 400:
        try:
            detail = resp.json()
            message = detail.get("error", resp.text)
        except ValueError:
            message = resp.text
        raise HFInferenceError(resp.status_code, message)

    if content_type.startswith("image/"):
        encoded = base64.b64encode(resp.content).decode("utf-8")
        return {"type": "image", "data": f"data:{content_type};base64,{encoded}"}

    if content_type.startswith("video/"):
        encoded = base64.b64encode(resp.content).decode("utf-8")
        return {"type": "video", "data": f"data:{content_type};base64,{encoded}"}

    try:
        return {"type": "json", "data": resp.json()}
    except ValueError:
        return {"type": "text", "data": resp.text}
