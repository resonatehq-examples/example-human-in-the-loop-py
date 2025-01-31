# Dead Simple Human-in-the-Loop Workflows with [Resonate](https://github.com/resonatehq/resonate)

This example application demonstrates how straightforward it is to implement business logic involving human judgment between executions. While such requirements are common and valuable, traditional implementations often face challenges: fragmented handlers reacting to unpredictable events, complex state management, and scalability constraints.

With Resonate, you write **procedural** code that pauses indefinitely while awaiting human input. This approach allows developers to express business logic for cloud-native environments as simply as writing their first scripts—no boilerplate, no distributed systems jargon, just clean code.

Take an email-based approval system requiring human input that might take days, months, or even years. Here’s how it looks when deployed in a serverless environment:

```python
@resonate.register()
def auth_handler(ctx: Context, email: str) -> Generator[Yieldable, Any, str]:
    promise: Promise[bool] = yield ctx.promise()
    yield ctx.lfc(send_email, promise.id, email)
    value: bool = yield promise
    if value:
        return "You’re authorized!"
    return "Not authorized :("
```

The workflow sends an email with **Approve** or **Reject** buttons, then waits indefinitely for a response. When the recipient clicks a button, execution resumes seamlessly. In a serverless environment, the initial Lambda instance shuts down once it can no longer make progress, and a fresh instance spins up the moment the user resolves the promise via the email action.

## Running the demo

### Application Architecture

This example consists of three components:

- **Sender**: Initiates approval workflows
- **Listener**: Monitors for promise resolutions
- **Auth Service**: Web server handling promise resolution via API

### Workflow Execution

1. **Start Services**
```bash
# Terminal 1 - Start Listener
uv run hitl-listen

# Terminal 2 - Start Auth Service
uv run hitl-auth-service
```
2. **Initiate Approval Workflow**
```bash
uv run hitl-auth <your-email@domain.com> # Creates a pending approval promise and sends email
```
3. Resolve Promise
   - Check Listener terminal for resolution links:
```bash
APPROVE: http://localhost:8000/approve?pid=<PROMISE_ID>
REJECT: http://localhost:8000/reject?pid=<PROMISE_ID>
```
   - Click either link to continue workflow execution
4. **Observe Completion**
   The Sender workflow resumes automatically after resolution, showing final authorization status.
