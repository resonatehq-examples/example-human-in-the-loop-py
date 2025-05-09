from resonate.message_sources.poller import Poller
from resonate.stores.remote import RemoteStore
from resonate import Resonate
from threading import Event

app_node_id = "worker"
app_node_group = "worker"

resonate = Resonate(
    store=RemoteStore(host="http://localhost", port="8001"),
    message_source=Poller(
        host="http://localhost", port="8002", id=app_node_id, group=app_node_group
    ),
)


def send_email(_, promise_id):
    """
    simulates sending an email by printing a message to the terminal
    """
    email_content = f"to unblock the workflow, please click the link below:\n http://localhost:5001/unblock-workflow?promise_id={promise_id}"
    print(email_content)


@resonate.register()
def foo(ctx):
    blocking_promise = yield ctx.promise()
    yield ctx.lfc(send_email, blocking_promise.id)
    print("workflow blocked, waiting on human interaction")
    # wait for the promise to be resolved
    yield blocking_promise
    print("workflow unblocked, promise resolved")
    return {"message": "workflow completed"}


def main() -> None:
    resonate.start()
    print("worker running")
    Event().wait()


if __name__ == "__main__":
    main()
