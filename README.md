![resonate example app banner](/assets/resonate-example-app-readme-banner.png)

# Human-In-The-Loop

![human in the loop banner](/assets/human-in-the-loop-banner.png)

**Resonate Python SDK**

This example showcases Resonate's ability to block a function execution's progress while awaiting on an action/input from a human.

Instructions on [How to run this example](#how-to-run-the-example) are below.

## Indefinite function suspension

The Human-In-The-Loop example showcases how Resonate enables a function to suspend execution for an indefinite amount of time. That is — where the function yields the promsie, the function stops executing and will only resume when the promise resolves.

```python
def foo(ctx, workflow_id):
    blocking_promise = yield ctx.promise()
    # ...
    # wait for the promise to be resolved
    yield blocking_promise
    # ...
```

This enables a wide range of use cases where a function may depend on a human interaction or human input for it to continue.

Use cases like this have tradionally been quite complex to solve for, requiring the steps to be broken up and triggered by schedules or a queuing architecture.

Resonate pushes that complexity into the platform, enabling a much simpler developer experience for these use cases.

## Deduplication

With Resonate, each function invocation pairs with a promise.
Each promise has a unique ID in the system.

The Resonate system deduplicates on the promise ID and will either reconnect to an PENDING progress, or return the result of the RESOLVED promise.

This example showcases how this works in the gateway:

```python
@app.route("/start-workflow", methods=["POST"])
def start_workflow_route_handler():
    # invoke with the provided workflow id and get a handle to that promise
    handle = resonate.options(target="poll://worker").rpc(data["workflow_id"], "foo", data["workflow_id"])
    # check if the workflow is done
    if handle.done():
        # if the workflow is done, return the result
        return jsonify({"message": handle.result()})
    # if the workflow is not done yet, return a message that the workflow started
    return jsonify({"message": f"workflow {data["workflow_id"]} started"}), 200
```

## Load balancing and recovery

This example is capable of showcasing Resonate's automatic loadbalancing and recovery.

Run multiple workers and start multiple workflows.
You will eventually see each worker start executing a workflow.

Try killing one of the workers while the workflow is blocked and watch it recover on the other worker.

## How to run the example

This example application uses [uv](https://docs.astral.sh/uv/) as the Python environment and package manager.

After cloning this repo, change directory into the root of the project and run the following command to install dependencies:

```shell
uv sync
```

This example application requires that a [Resonate Server](https://docs.resonatehq.io/get-started/server-quickstart) is running locally.

You will need 3 terminals to run this example, one for the HTTP Gateway, one for the Worker, and one to send a cURL request. This does not include the terminal where you might have started the Resonate Server.

In _Terminal 1_, start the HTTP Gateway:

```shell
uv run gateway
```

In _Terminal 2_, start the Worker:

```shell
uv run worker
```

In _Terminal 3_, send the cURL request to start the workflow:

```shell
curl -X POST http://localhost:5001/start-workflow -H "Content-Type: application/json" -d '{"workflow_id": "hitl-001"}'
```

The worker will print a link that you can navigate to in your browser, which sends another request to the gateway, resolving the blocking promise and allowing the workflow to complete.
