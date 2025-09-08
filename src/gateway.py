from flask import Flask, request, jsonify
from resonate import Resonate

app_node_group = "gateway"

app = Flask(app_node_group)

resonate = Resonate.remote(host="http://localhost", group=app_node_group)


@app.route("/start-workflow", methods=["POST"])
def start_workflow_route_handler():
    """
    start a workflow using Resonate
    """
    data = request.get_json()
    if "workflow_id" not in data:
        return jsonify({"error": "workflow_id is required"}), 400
    handle = resonate.options(target="poll://any@worker").begin_rpc(data["workflow_id"], "foo", data["workflow_id"])
    # check if the workflow is done
    if handle.done():
        # if the workflow is done, return the result
        return jsonify({"message": handle.result()})
    # if the workflow is not done yet, return a message
    return jsonify({"message": f"workflow {data["workflow_id"]} started"}), 200


@app.route("/unblock-workflow", methods=["GET"])
def unblock_workflow_route_handler():
    """
    unblock a workflow by resolving a promise
    """
    promise_id = request.args.get("promise_id")
    if not promise_id:
        return jsonify({"error": "promise_id is required"}), 400
    # resolve the promise
    resonate.promises.resolve(id=promise_id, ikey=promise_id)
    return jsonify({"message": "workflow unblocked"}), 200


def main() -> None:
    resonate.start()
    print("http gateway running")
    app.run(host="127.0.0.1", port=5001)


if __name__ == "__main__":
    main()
