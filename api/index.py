"""
Vercel Python serverless entrypoint. Vercel auto-detects any file under
/api that exports an ASGI `app` and serves it as a function — this just
re-exports the real FastAPI app from backend/app/main.py, adding the
backend directory to sys.path since Vercel's Python runtime does not
treat this monorepo's sibling folders as importable packages by default.
"""

import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from app.main import app  # noqa: E402
