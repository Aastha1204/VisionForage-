from fastapi import APIRouter, File, Form, HTTPException, UploadFile

import base64
import json

from app.core.hf_client import HFInferenceError, query_binary, query_image_with_text, query_json
from app.core.space_client import (
    SpaceInferenceError,
    call_classic_space,
    call_queue_space,
    call_queue_space_text,
    call_space_no_input,
    fetch_file_as_data_url,
    query_space_image_output,
    query_space_text_output,
)
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
    space_host = task.get("space_host")

    try:
        if space_host and task.get("space_protocol") == "classic" and input_type == "video":
            if not file:
                raise HTTPException(status_code=400, detail="A video file is required for this task.")
            video_bytes = await file.read()
            b64 = base64.b64encode(video_bytes).decode("utf-8")
            content_type = file.content_type or "video/mp4"
            video_file = {
                "name": file.filename or "video.mp4",
                "data": f"data:{content_type};base64,{b64}",
                "is_file": False,
            }
            space_result = call_classic_space(space_host, task["space_fn_index"], [video_file])
            result = {"type": "json", "data": space_result[0]}

        elif space_host and task.get("space_protocol") == "classic":
            if not file:
                raise HTTPException(status_code=400, detail="An image file is required for this task.")
            if not candidate_labels:
                raise HTTPException(status_code=400, detail="Candidate labels are required for this task.")
            image_bytes = await file.read()
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            data_uri = f"data:{file.content_type or 'image/jpeg'};base64,{b64}"
            labels = [label.strip() for label in candidate_labels.split(",") if label.strip()]
            prompt_str = " . ".join(labels) + " ."
            space_result = call_classic_space(
                space_host, task["space_fn_index"], [data_uri, prompt_str, 0.25, 0.25]
            )
            result = {"type": "image", "data": space_result[0]}

        elif space_host and task.get("space_protocol") == "queue":
            if not file:
                raise HTTPException(status_code=400, detail="An image file is required for this task.")
            image_bytes = await file.read()

            if task_id == "mask-generation":
                build_data = lambda file_data: ["tiny", "mask generation", file_data, None]  # noqa: E731
            else:
                raise HTTPException(status_code=500, detail=f"No queue-protocol handler wired for '{task_id}'")

            space_result = call_queue_space(
                space_host,
                task["space_fn_index"],
                image_bytes,
                build_data,
                orig_name=file.filename or "image.jpg",
                content_type=file.content_type or "image/jpeg",
            )
            result = {"type": "image", "data": fetch_file_as_data_url(space_result[0]["url"])}

        elif space_host and task.get("space_protocol") == "queue_text":
            if task_id == "text-to-video":
                if not prompt:
                    raise HTTPException(status_code=400, detail="A text prompt is required for this task.")
                data = [prompt, "ToonYou", "", 4]
            else:
                raise HTTPException(status_code=500, detail=f"No queue_text handler wired for '{task_id}'")

            space_result = call_queue_space_text(space_host, task["space_fn_index"], data)
            video_ref = space_result[0]["video"] if isinstance(space_result[0], dict) else space_result[0]
            result = {"type": "video", "data": fetch_file_as_data_url(video_ref["url"])}

        elif space_host and input_type == "none":
            space_result = call_space_no_input(space_host, task["space_api_name"], [25])
            result = {"type": "image", "data": fetch_file_as_data_url(space_result[0]["url"])}

        elif space_host:
            if not file:
                raise HTTPException(status_code=400, detail="An image file is required for this task.")
            image_bytes = await file.read()

            space_extra_args = None
            output_index = 0
            if task_id == "keypoint-detection":
                space_extra_args = [0.6, True, True]
            elif task_id == "image-to-image":
                if not prompt:
                    raise HTTPException(status_code=400, detail="A prompt describing the edit is required.")
                space_extra_args = [prompt, 50, "Randomize Seed", 1371, "Fix CFG", 7.5, 1.5]
                output_index = 3

            if task["output_type"] == "image":
                image_data = query_space_image_output(
                    space_host, task["space_api_name"], image_bytes, space_extra_args, output_index
                )
                result = {"type": "image", "data": image_data}
            elif task["output_type"] == "json":
                raw = query_space_text_output(space_host, task["space_api_name"], image_bytes)
                try:
                    result = {"type": "json", "data": json.loads(raw)}
                except (TypeError, json.JSONDecodeError):
                    result = {"type": "text", "data": raw}
            else:
                caption = query_space_text_output(space_host, task["space_api_name"], image_bytes)
                result = {"type": "text", "data": caption}

        elif input_type == "image":
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

    except SpaceInferenceError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"{exc.message} (served via a public Hugging Face Space, which can be slow to "
            "wake up or occasionally unavailable — try again in a moment).",
        )

    return {"task_id": task_id, "model": model, "result": result}
