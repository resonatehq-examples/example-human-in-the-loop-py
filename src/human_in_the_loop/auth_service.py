import json
from fastapi import FastAPI
import uvicorn
from resonate.stores import RemoteStore

resonate_store = RemoteStore()
# Create a FastAPI app instance
app = FastAPI()


# Define a sample route


@app.get("/")
def read_root(promise_id: str, value: bool):
    resonate_store.promises.resolve(
        id=promise_id, ikey=None, strict=False, headers=None, data=json.dumps(value)
    )
    return {"success": "We have received you response. Thanks!"}


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
