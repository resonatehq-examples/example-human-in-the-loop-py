import socket
from typing import Any, Generator
from resonate import Promise, Resonate, Context
from resonate.task_sources import Poller
from typer import Typer
from resonate.typing import Yieldable
from ._constants import HOST, PORT

app = Typer()
resonate = Resonate(task_source=Poller(group="auth-service"))


def send_email(ctx: Context, promise_id: str, email: str) -> None:
    """
    Simulates sending an email.

    For the sake of the example we'll just print in the terminal,
    but you can imagine doing an API request to Gmail, or sending
    and SMS to a phone number.
    """
    msg = f"""
-------------------------------------------------------------------------------------------------------------
|You've received a new email {email}!                                                                       |
|                                                                                                           |
|Seems someone needs you to confirm your email before continue. To confirm                                  |
|please click here: [ http://127.0.0.1:8000/?promise_id={promise_id}&approved=true ]                        |
|                                                                                                           |
|In case you want to not confirm, click here: [ http://127.0.0.1:8000/?promise_id={promise_id}&approved=false ]  |
-------------------------------------------------------------------------------------------------------------
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(msg.encode() + b"\n")  # Add newline to separate messages


@resonate.register()
def auth_handler(ctx: Context, email: str) -> Generator[Yieldable, Any, str]:
    promise: Promise[bool] = yield ctx.promise()
    yield ctx.lfc(send_email, promise.id, email)
    value: bool = yield promise
    if value:
        return "You are authorize!"

    return "Not authorized :("


@app.command()
def auth(email: str) -> None:
    handle = resonate.run(f"auth-{email}", auth_handler, email)
    print(handle.result())


def main() -> None:
    app()
