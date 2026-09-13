from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.hf_client import HFInferenceError, query_binary, query_image_with_text, query_json
from app.core.tasks import TASKS_BY_ID

router = APIRouter(prefix="/api/infer", tags=["infer"])


@router.post("/{task_id}")
async def run_inference(
    task_id: str,
    file: UploadFile | None = File(default=None),
    prompt: str | None = Form(default=None),
    candidate_labels: str | None = Form(default=None),
    model_id: str | None = Form(default=None),
):
    task = TASKS_BY_ID.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Unknown task '{task_id}'")

    model = model_id.strip() if model_id else task["default_model"]
    input_type = task["input_type"]

    try:
        if input_type == "image":
            if not file:
                raise HTTPException(status_code=400, detail="An image file is required for this task.")
            image_bytes = await file.read()
            result = query_binary(model, image_bytes, file.content_type or "image/jpeg")

        elif input_type == "video":
            if not file:
                raise HTTPException(status_code=400, detail="A video file is required for this task.")
            video_bytes = await file.read()
            result = query_binary(model, video_bytes, file.content_type or "video/mp4")

        elif input_type == "text":
            if not prompt:
                raise HTTPException(status_code=400, detail="A text prompt is required for this task.")
            result = query_json(model, {"inputs": prompt})

        elif input_type == "none":
            result = query_json(model, {"inputs": ""})

        elif input_type == "image_text":
            if not file:
                raise HTTPException(status_code=400, detail="An image file is required for this task.")
            image_bytes = await file.read()
            extra_fields: dict = {}
            if candidate_labels:
                extra_fields["parameters"] = {
                    "candidate_labels": [label.strip() for label in candidate_labels.split(",") if label.strip()]
                }
            elif prompt:
                extra_fields["parameters"] = {"prompt": prompt}
            result = query_image_with_text(model, image_bytes, extra_fields)

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported input type '{input_type}'")

    except HFInferenceError as exc:
        hint = (
            " This task is experimental and may require a dedicated Hugging Face "
            "Inference Endpoint rather than the free serverless API — try overriding "
            "the model ID with your own endpoint, or check the model's status on huggingface.co."
            if task["experimental"]
            else ""
        )
        raise HTTPException(status_code=exc.status_code or 502, detail=f"{exc.message}{hint}")

    return {"task_id": task_id, "model": model, "result": result}
