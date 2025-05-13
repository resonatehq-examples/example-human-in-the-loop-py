from resonate.message_sources.poller import Poller
from resonate import Resonate
from threading import Event

resonate = Resonate.remote(host="http://localhost", group="worker")


def send_email(_, promise_id):
    """
    simulates sending an email by printing a message to the terminal
    """
    email_content = f"to unblock the workflow, please click the link below:\n http://localhost:5001/unblock-workflow?promise_id={promise_id}"
    print(email_content)


@resonate.register()
def foo(ctx, workflow_id):
    blocking_promise = yield ctx.promise()
    yield ctx.lfc(send_email, blocking_promise.id)
    print(f"workflow {workflow_id} blocked, waiting on human interaction")
    # wait for the promise to be resolved
    yield blocking_promise
    print(f"workflow {workflow_id} unblocked, promise resolved")
    return {"message": f"workflow {workflow_id} completed"}


def main() -> None:
    resonate.start()
    print("worker running")
    Event().wait()


if __name__ == "__main__":
    main()
