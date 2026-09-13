# VisionForge

A single dashboard covering every Hugging Face computer-vision task category —
depth estimation, classification, segmentation, detection, image/video/3D
generation, zero-shot tasks, and more — backed by the HF serverless Inference
API, with a plug-in architecture so adding a new task is a one-line registry
entry.

## Structure

- `backend/` — FastAPI service. `app/core/tasks.py` is the single source of
  truth for every task (label, default model, input/output shape). Requests
  are proxied to `https://router.huggingface.co/hf-inference/models/<model_id>`
  (HF's current serverless Inference API — the old `api-inference.huggingface.co`
  host is retired).
- `frontend/` — React + Vite dashboard. Renders the task grid, an
  upload/prompt form per task, and a result viewer (image/video/JSON/text).

## Running locally

**Backend**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then paste your Hugging Face token into HF_TOKEN
uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

## Notes on task coverage

HF's free `hf-inference` serverless provider has been narrowing which
pipeline tasks it hosts. As of this writing, only four tasks have live,
working default models on the free tier — all verified end-to-end with a
real API call:

| Task | Default model | Status |
|---|---|---|
| Image Classification | `google/vit-base-patch16-224` | ✅ verified live |
| Object Detection | `facebook/detr-resnet-50` | ✅ verified live |
| Image Segmentation | `nvidia/segformer-b0-finetuned-ade-512-512` | ✅ verified live |
| Text-to-Image | `stabilityai/stable-diffusion-3-medium-diffusers` | ✅ verified live |

Every other task (depth estimation, image-to-text, zero-shot classification/
detection, image feature extraction, and everything video/3D) is marked
**experimental** in the UI — querying the HF model API
(`huggingface.co/api/models?pipeline_tag=<task>&inference_provider=hf-inference`)
turns up **zero** publicly hosted models for these on the free tier right
now, even though their default model IDs are otherwise correct, real models.
For those, override the "Model ID" field on the task page with your own paid
Hugging Face Inference Endpoint, or a Space that exposes a compatible API.

Since providers and model availability change over time, re-run that same
model-listing query against a task's `pipeline_tag` if a default ever starts
failing with "Model not supported by provider hf-inference" or "deprecated".
