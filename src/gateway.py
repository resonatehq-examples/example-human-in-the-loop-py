"""HTTP gateway for the Human-in-the-Loop example.

Accepts POST /start-workflow to kick off a durable workflow and
GET /unblock-workflow?promise_id=<id> to resolve the blocking promise
and allow the workflow to continue.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, HTTPException, Request
from resonate.resonate import Resonate
from resonate.types import Value
import uvicorn

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# Import the workflow function so it can be registered on the Resonate instance.
from .worker import foo

# ---------------------------------------------------------------------------
# Resonate instance — constructed inside the lifespan (requires event loop)
# ---------------------------------------------------------------------------

_resonate: Resonate | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _resonate
    _resonate = Resonate(url=os.environ.get("RESONATE_URL", "http://localhost:8001"))
    _resonate.register(foo)
    print("http gateway running", flush=True)
    yield
    await _resonate.stop()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(lifespan=lifespan)


@app.post("/start-workflow")
async def start_workflow(request: Request) -> dict[str, Any]:
    """Start a durable workflow identified by workflow_id.

    If the same workflow_id is sent again, Resonate deduplicates and
    reconnects to the existing (PENDING) workflow without re-running it.
    Returns immediately — the workflow runs asynchronously on the worker.
    """
    assert _resonate is not None, "Resonate not initialised"
    data: dict[str, Any] = await request.json()
    if "workflow_id" not in data:
        raise HTTPException(status_code=400, detail="workflow_id is required")

    workflow_id: str = data["workflow_id"]
    # Fire and forget — r.run is synchronous; the workflow executes on the worker.
    _resonate.run(workflow_id, foo, workflow_id)

    return {"message": f"workflow {workflow_id} started"}


@app.get("/unblock-workflow")
async def unblock_workflow(promise_id: str | None = None) -> dict[str, Any]:
    """Resolve a blocking durable promise to unblock a suspended workflow."""
    assert _resonate is not None, "Resonate not initialised"
    if not promise_id:
        raise HTTPException(status_code=400, detail="promise_id is required")

    await _resonate.promises.resolve(promise_id, Value(data=None))
    return {"message": "workflow unblocked"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=5001, log_level="warning")


if __name__ == "__main__":
    main()
