# Pipeline Sidecar Spec — User Context & Callback API

**Status**: Proposal
**Date**: 2026-02-11
**Audience**: Pipeline server (`open-webui/pipelines`) developers

## Overview

Open WebUI now injects user identity and callback metadata into every request
sent to pipeline servers. This enables pipelines to:

- Know **who** is calling (user id, name, email, role)
- **Log and audit** pipeline usage per user
- **Call back** to Open WebUI APIs on behalf of the authenticated user
  (read/write files, query knowledge, invoke models)

The pipeline server is treated as a **trusted sidecar** — it runs in the same
deployment as Open WebUI and is operator-deployed (no dynamic installation from
untrusted sources).

## Filter Deprecation

Open WebUI no longer uses the `inlet`/`outlet` filter system. All pipeline
logic goes through `pipe()`. A pipe that needs to wrap an existing model can
call it via the callback API (see examples below).

The filter endpoints (`/{id}/filter/inlet`, `/{id}/filter/outlet`) are no
longer called by Open WebUI. Pipeline servers may keep them for backwards
compatibility but they will not receive traffic from this fork.

## What Open WebUI Sends

### `POST /chat/completions`

The request body includes two additional top-level fields for pipeline models:

```json
{
  "model": "pipeline-id",
  "messages": [{"role": "user", "content": "hello"}],
  "stream": true,

  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Jane Doe",
    "email": "jane@example.com",
    "role": "user"
  },

  "__openwebui": {
    "base_url": "http://localhost:8080",
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "chat_id": "chat-uuid-here"
  }
}
```

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `user.id` | `string` | User UUID |
| `user.name` | `string` | Display name |
| `user.email` | `string` | Email address |
| `user.role` | `string` | `"user"` or `"admin"` |
| `__openwebui.base_url` | `string` | Open WebUI API base URL |
| `__openwebui.token` | `string` | User's JWT for API callbacks |
| `__openwebui.chat_id` | `string\|null` | Current chat UUID |

## Required Changes

### 1. Pass `user` to `pipe()` in `/chat/completions` handler

The `user` field is already in the request body but is currently ignored by the
`/chat/completions` handler. Extract it and pass it to `pipe()`.

**Current** (main.py, chat completions handler):
```python
res = pipe(
    user_message=user_message,
    model_id=pipeline_id,
    messages=messages,
    body=form_data.model_dump(),
)
```

**Proposed**:
```python
body = form_data.model_dump()
user = body.get("user")

res = pipe(
    user_message=user_message,
    model_id=pipeline_id,
    messages=messages,
    body=body,
    user=user,
)
```

Apply this to both the streaming and non-streaming code paths.

### 2. Add request logging

Log user identity in the `/chat/completions` handler for audit:

```python
user = body.get("user")
log.info(
    f"chat/completions: pipeline={pipeline_id} "
    f"user={user.get('id') if user else 'anonymous'}"
)
```

## Backwards Compatibility

All new fields are optional with `None` defaults:

- **Existing pipelines** continue to work without changes. The `user` kwarg
  defaults to `None`, and `__openwebui` is simply present in `body` for
  pipelines that want it.

- **Non-Open WebUI callers** (direct API usage, testing) work fine — `user`
  will be `None` and `__openwebui` will be absent.

- The `pipe()` signature change is backwards-compatible because `user` is
  passed as a keyword argument:

  ```python
  # Still works — ignores unknown kwargs
  def pipe(self, user_message, model_id, messages, body):
      ...

  # Opt-in to user context
  def pipe(self, user_message, model_id, messages, body, user=None):
      ...
  ```

## Callback API Usage

Pipelines can use `__openwebui` to call Open WebUI's REST API on behalf of
the authenticated user. The token carries the user's permissions.

### Example: Read a file

```python
import requests

def pipe(self, user_message, model_id, messages, body, user=None):
    ow = body.get("__openwebui", {})
    base_url = ow.get("base_url")
    token = ow.get("token")

    if base_url and token:
        r = requests.get(
            f"{base_url}/api/v1/files/{file_id}/content",
            headers={"Authorization": f"Bearer {token}"},
        )
        r.raise_for_status()
        file_data = r.content
```

### Example: Upload a file

```python
def pipe(self, user_message, model_id, messages, body, user=None):
    ow = body.get("__openwebui", {})

    r = requests.post(
        f"{ow['base_url']}/api/v1/files/",
        headers={"Authorization": f"Bearer {ow['token']}"},
        files={"file": ("report.csv", csv_bytes, "text/csv")},
    )
    uploaded = r.json()
```

### Example: List user's files

```python
def pipe(self, user_message, model_id, messages, body, user=None):
    ow = body.get("__openwebui", {})

    r = requests.get(
        f"{ow['base_url']}/api/v1/files/",
        headers={"Authorization": f"Bearer {ow['token']}"},
    )
    files = r.json()
```

### Available Open WebUI API Endpoints

Any endpoint in Open WebUI's REST API is callable. Common ones:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/files/` | GET | List user's files |
| `/api/v1/files/` | POST | Upload a file |
| `/api/v1/files/{id}/content` | GET | Download file content |
| `/api/v1/files/{id}` | DELETE | Delete a file |
| `/api/v1/knowledge/` | GET | List knowledge bases |
| `/api/v1/knowledge/{id}` | GET | Get knowledge base details |
| `/api/v1/chats/` | GET | List user's chats |
| `/api/v1/models` | GET | List available models |

## Optional: `OpenWebUIClient` Helper

A convenience wrapper for pipelines that frequently call back to Open WebUI:

```python
import requests

class OpenWebUIClient:
    """Helper for pipelines to access Open WebUI services."""

    def __init__(self, body: dict):
        meta = body.get("__openwebui", {})
        self.base_url = (meta.get("base_url") or "").rstrip("/")
        self.token = meta.get("token")
        self.chat_id = meta.get("chat_id")
        self.user = body.get("user")

    @property
    def available(self) -> bool:
        return bool(self.base_url and self.token)

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    def get_file(self, file_id: str) -> bytes:
        r = requests.get(
            f"{self.base_url}/api/v1/files/{file_id}/content",
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.content

    def upload_file(self, filename: str, content: bytes,
                    content_type: str = "application/octet-stream") -> dict:
        r = requests.post(
            f"{self.base_url}/api/v1/files/",
            headers=self._headers(),
            files={"file": (filename, content, content_type)},
        )
        r.raise_for_status()
        return r.json()

    def list_files(self) -> list:
        r = requests.get(
            f"{self.base_url}/api/v1/files/",
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    def delete_file(self, file_id: str) -> dict:
        r = requests.delete(
            f"{self.base_url}/api/v1/files/{file_id}",
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()
```

Usage:

```python
class Pipeline:
    def pipe(self, user_message, model_id, messages, body, user=None):
        client = OpenWebUIClient(body)

        if not client.available:
            yield "Pipeline callback not available."
            return

        # Access files, knowledge, etc.
        files = client.list_files()
        yield f"You have {len(files)} files.\n"
```

## Deployment Configuration

### `OPENWEBUI_API_URL` (Open WebUI side)

When the pipeline server runs in a different container or host, set this env var
on the Open WebUI instance so pipelines receive a reachable callback URL:

```bash
# Open WebUI env
OPENWEBUI_API_URL=http://open-webui:8080
```

If unset, defaults to `request.base_url` (works when both services share
the same host/network).
