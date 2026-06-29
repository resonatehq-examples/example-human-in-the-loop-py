"""Worker for the Human-in-the-Loop example.

Registers the ``foo`` workflow with Resonate and polls for tasks.
The workflow suspends on a durable promise until an external caller
(e.g. a human clicking an email link) resolves it via the gateway's
/unblock-workflow endpoint.
"""
from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

from resonate.resonate import Resonate

if TYPE_CHECKING:
    from resonate.context import Context


# ---------------------------------------------------------------------------
# Leaf functions
# ---------------------------------------------------------------------------


async def send_email(ctx: Context, promise_id: str) -> None:
    """Simulate sending an email with an unblock link."""
    email_content = (
        f"to unblock the workflow, please click the link below:\n"
        f" http://localhost:5001/unblock-workflow?promise_id={promise_id}"
    )
    print(email_content, flush=True)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


async def foo(ctx: Context, workflow_id: str) -> dict[str, str]:
    """Durable workflow that suspends until a human resolves a promise."""
    # Create a durable promise; the workflow suspends here until it resolves.
    blocking_promise = ctx.promise()
    promise_id = await blocking_promise.id()

    # Notify the human (or external system) with the promise id they must resolve.
    await ctx.run(send_email, promise_id)

    print(f"workflow {workflow_id} blocked, waiting on human interaction", flush=True)

    # Suspend until the external party resolves the promise.
    await blocking_promise

    print(f"workflow {workflow_id} unblocked, promise resolved", flush=True)
    return {"message": f"workflow {workflow_id} completed"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def _run() -> None:
    r = Resonate(
        url=os.environ.get("RESONATE_URL", "http://localhost:8001"),
        group="worker",
    )
    r.register(foo)
    print("worker running", flush=True)
    await asyncio.Event().wait()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
