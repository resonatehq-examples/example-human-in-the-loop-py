# Human-In-The-Loop | Resonate example application

This example showcases Resonate's ability to block a function execution's progress while awaiting on an action/input from a human.

## Project prerequisites

This example application uses [uv](https://docs.astral.sh/uv/) as the Python environment and package manager.

After cloning this repo, change directory into the root of the project and run the following command to install dependencies:

```shell
uv sync
```

This example application requires that a [Resonate Server](https://docs.resonatehq.io/get-started/server-quickstart) is running locally.

## How to run the example

You will need 3 terminals to run this example, one for the HTTP Gateway, one for the Worker, and one to send a cURL request. This does not include the terminal where you might have started the Resonate Server.

In _Terminal 1_, start the HTTP Gateway:

```shell
uv run gateway
```

In _Terminal 2_, start the Worker:

```shell
uv run Worker
```

In _Terminal 3_, send the cURL request:

```shell
curl -X POST http://localhost:5001/start-workflow -H "Content-Type: application/json" -d '{"workflow_id": "hitl-001"}'
```
