"""
Central registry of every computer-vision task VisionForge exposes.

Each entry drives both the backend inference call and the frontend UI
(input widget, result renderer) — add a new task here and it shows up
everywhere automatically.

input_type:  "image" | "text" | "image_text" | "video"
output_type: "image" | "json" | "text"
experimental: True means the task is not reliably available on HF's free
              serverless Inference API and typically needs a dedicated
              Inference Endpoint / Space — the UI will show a warning
              and let the user supply their own model_id / endpoint.
"""

from typing import TypedDict


class TaskDef(TypedDict):
    id: str
    label: str
    category: str
    description: str
    default_model: str
    input_type: str
    output_type: str
    experimental: bool


TASKS: list[TaskDef] = [
    {
        "id": "depth-estimation",
        "label": "Depth Estimation",
        "category": "Computer Vision",
        "description": "Predict per-pixel depth from a single image.",
        "default_model": "Intel/dpt-hybrid-midas",
        "input_type": "image",
        "output_type": "image",
        "experimental": True,
    },
    {
        "id": "image-classification",
        "label": "Image Classification",
        "category": "Computer Vision",
        "description": "Assign the most likely labels to an image.",
        "default_model": "google/vit-base-patch16-224",
        "input_type": "image",
        "output_type": "json",
        "experimental": False,
    },
    {
        "id": "image-feature-extraction",
        "label": "Image Feature Extraction",
        "category": "Computer Vision",
        "description": "Turn an image into a dense embedding vector.",
        "default_model": "google/vit-base-patch16-224",
        "input_type": "image",
        "output_type": "json",
        "experimental": True,
    },
    {
        "id": "image-segmentation",
        "label": "Image Segmentation",
        "category": "Computer Vision",
        "description": "Segment an image into labeled regions/masks.",
        "default_model": "nvidia/segformer-b0-finetuned-ade-512-512",
        "input_type": "image",
        "output_type": "json",
        "experimental": False,
    },
    {
        "id": "image-to-image",
        "label": "Image-to-Image",
        "category": "Computer Vision",
        "description": "Transform an image guided by a text prompt.",
        "default_model": "timbrooks/instruct-pix2pix",
        "input_type": "image_text",
        "output_type": "image",
        "experimental": True,
    },
    {
        "id": "image-to-text",
        "label": "Image-to-Text",
        "category": "Computer Vision",
        "description": "Generate a caption describing an image.",
        "default_model": "Salesforce/blip-image-captioning-base",
        "input_type": "image",
        "output_type": "text",
        "experimental": True,
    },
    {
        "id": "image-to-video",
        "label": "Image-to-Video",
        "category": "Computer Vision",
        "description": "Animate a still image into a short video.",
        "default_model": "stabilityai/stable-video-diffusion-img2vid-xt",
        "input_type": "image",
        "output_type": "image",
        "experimental": True,
    },
    {
        "id": "keypoint-detection",
        "label": "Keypoint Detection",
        "category": "Computer Vision",
        "description": "Locate skeletal/landmark keypoints in an image.",
        "default_model": "usyd-community/vitpose-base-simple",
        "input_type": "image",
        "output_type": "json",
        "experimental": True,
    },
    {
        "id": "mask-generation",
        "label": "Mask Generation",
        "category": "Computer Vision",
        "description": "Generate object masks (Segment Anything style).",
        "default_model": "facebook/sam-vit-base",
        "input_type": "image",
        "output_type": "json",
        "experimental": True,
    },
    {
        "id": "object-detection",
        "label": "Object Detection",
        "category": "Computer Vision",
        "description": "Detect objects and draw bounding boxes.",
        "default_model": "facebook/detr-resnet-50",
        "input_type": "image",
        "output_type": "json",
        "experimental": False,
    },
    {
        "id": "video-classification",
        "label": "Video Classification",
        "category": "Computer Vision",
        "description": "Classify the action/content of a short video.",
        "default_model": "MCG-NJU/videomae-base-finetuned-kinetics",
        "input_type": "video",
        "output_type": "json",
        "experimental": True,
    },
    {
        "id": "text-to-image",
        "label": "Text-to-Image",
        "category": "Computer Vision",
        "description": "Generate an image from a text prompt.",
        "default_model": "stabilityai/stable-diffusion-3-medium-diffusers",
        "input_type": "text",
        "output_type": "image",
        "experimental": False,
    },
    {
        "id": "text-to-video",
        "label": "Text-to-Video",
        "category": "Computer Vision",
        "description": "Generate a short video from a text prompt.",
        "default_model": "damo-vilab/text-to-video-ms-1.7b",
        "input_type": "text",
        "output_type": "image",
        "experimental": True,
    },
    {
        "id": "unconditional-image-generation",
        "label": "Unconditional Image Generation",
        "category": "Computer Vision",
        "description": "Generate an image with no input (pure sampling).",
        "default_model": "google/ddpm-celebahq-256",
        "input_type": "none",
        "output_type": "image",
        "experimental": True,
    },
    {
        "id": "video-to-video",
        "label": "Video-to-Video",
        "category": "Computer Vision",
        "description": "Transform an input video into a new video.",
        "default_model": "custom/video-to-video",
        "input_type": "video",
        "output_type": "image",
        "experimental": True,
    },
    {
        "id": "zero-shot-image-classification",
        "label": "Zero-Shot Image Classification",
        "category": "Computer Vision",
        "description": "Classify an image against labels you supply on the fly.",
        "default_model": "openai/clip-vit-base-patch32",
        "input_type": "image_text",
        "output_type": "json",
        "experimental": True,
    },
    {
        "id": "zero-shot-object-detection",
        "label": "Zero-Shot Object Detection",
        "category": "Computer Vision",
        "description": "Detect objects matching labels you supply on the fly.",
        "default_model": "google/owlvit-base-patch32",
        "input_type": "image_text",
        "output_type": "json",
        "experimental": True,
    },
    {
        "id": "text-to-3d",
        "label": "Text-to-3D",
        "category": "Computer Vision",
        "description": "Generate a 3D asset from a text prompt.",
        "default_model": "openai/shap-e",
        "input_type": "text",
        "output_type": "json",
        "experimental": True,
    },
    {
        "id": "image-to-3d",
        "label": "Image-to-3D",
        "category": "Computer Vision",
        "description": "Reconstruct a 3D asset from a single image.",
        "default_model": "TencentARC/InstantMesh",
        "input_type": "image",
        "output_type": "json",
        "experimental": True,
    },
]

TASKS_BY_ID: dict[str, TaskDef] = {t["id"]: t for t in TASKS}
