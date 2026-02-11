from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
    APIRouter,
)
import logging
import requests
from typing import Optional

from open_webui.env import OPENWEBUI_API_URL

from open_webui.routers.openai import get_all_models_responses

from open_webui.utils.auth import get_admin_user

log = logging.getLogger(__name__)


##################################
#
# Pipeline Middleware
#
##################################


def get_openwebui_metadata(request: Request) -> dict:
    """Build __openwebui callback metadata for pipeline requests."""
    base_url = OPENWEBUI_API_URL or str(request.base_url).rstrip("/")
    token = None
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]
    return {
        "base_url": base_url,
        "token": token,
    }


##################################
#
# Pipelines Endpoints
#
##################################

router = APIRouter()


@router.get("/list")
async def get_pipelines_list(request: Request, user=Depends(get_admin_user)):
    responses = await get_all_models_responses(request, user)
    log.debug(f"get_pipelines_list: get_openai_models_responses returned {responses}")

    urlIdxs = [
        idx
        for idx, response in enumerate(responses)
        if response is not None and "pipelines" in response
    ]

    return {
        "data": [
            {
                "url": request.app.state.config.OPENAI_API_BASE_URLS[urlIdx],
                "idx": urlIdx,
            }
            for urlIdx in urlIdxs
        ]
    }


@router.get("/")
async def get_pipelines(
    request: Request, urlIdx: Optional[int] = None, user=Depends(get_admin_user)
):
    r = None
    try:
        url = request.app.state.config.OPENAI_API_BASE_URLS[urlIdx]
        key = request.app.state.config.OPENAI_API_KEYS[urlIdx]

        r = requests.get(f"{url}/pipelines", headers={"Authorization": f"Bearer {key}"})

        r.raise_for_status()
        data = r.json()

        return {**data}
    except Exception as e:
        # Handle connection error here
        log.exception(f"Connection error: {e}")

        detail = None
        if r is not None:
            try:
                res = r.json()
                if "detail" in res:
                    detail = res["detail"]
            except Exception:
                pass

        raise HTTPException(
            status_code=(r.status_code if r is not None else status.HTTP_404_NOT_FOUND),
            detail=detail if detail else "Pipeline not found",
        )


@router.get("/{pipeline_id}/valves")
async def get_pipeline_valves(
    request: Request,
    urlIdx: Optional[int],
    pipeline_id: str,
    user=Depends(get_admin_user),
):
    r = None
    try:
        url = request.app.state.config.OPENAI_API_BASE_URLS[urlIdx]
        key = request.app.state.config.OPENAI_API_KEYS[urlIdx]

        r = requests.get(
            f"{url}/{pipeline_id}/valves", headers={"Authorization": f"Bearer {key}"}
        )

        r.raise_for_status()
        data = r.json()

        return {**data}
    except Exception as e:
        # Handle connection error here
        log.exception(f"Connection error: {e}")

        detail = None
        if r is not None:
            try:
                res = r.json()
                if "detail" in res:
                    detail = res["detail"]
            except Exception:
                pass

        raise HTTPException(
            status_code=(r.status_code if r is not None else status.HTTP_404_NOT_FOUND),
            detail=detail if detail else "Pipeline not found",
        )


@router.get("/{pipeline_id}/valves/spec")
async def get_pipeline_valves_spec(
    request: Request,
    urlIdx: Optional[int],
    pipeline_id: str,
    user=Depends(get_admin_user),
):
    r = None
    try:
        url = request.app.state.config.OPENAI_API_BASE_URLS[urlIdx]
        key = request.app.state.config.OPENAI_API_KEYS[urlIdx]

        r = requests.get(
            f"{url}/{pipeline_id}/valves/spec",
            headers={"Authorization": f"Bearer {key}"},
        )

        r.raise_for_status()
        data = r.json()

        return {**data}
    except Exception as e:
        # Handle connection error here
        log.exception(f"Connection error: {e}")

        detail = None
        if r is not None:
            try:
                res = r.json()
                if "detail" in res:
                    detail = res["detail"]
            except Exception:
                pass

        raise HTTPException(
            status_code=(r.status_code if r is not None else status.HTTP_404_NOT_FOUND),
            detail=detail if detail else "Pipeline not found",
        )


@router.post("/{pipeline_id}/valves/update")
async def update_pipeline_valves(
    request: Request,
    urlIdx: Optional[int],
    pipeline_id: str,
    form_data: dict,
    user=Depends(get_admin_user),
):
    r = None
    try:
        url = request.app.state.config.OPENAI_API_BASE_URLS[urlIdx]
        key = request.app.state.config.OPENAI_API_KEYS[urlIdx]

        r = requests.post(
            f"{url}/{pipeline_id}/valves/update",
            headers={"Authorization": f"Bearer {key}"},
            json={**form_data},
        )

        r.raise_for_status()
        data = r.json()

        return {**data}
    except Exception as e:
        # Handle connection error here
        log.exception(f"Connection error: {e}")

        detail = None

        if r is not None:
            try:
                res = r.json()
                if "detail" in res:
                    detail = res["detail"]
            except Exception:
                pass

        raise HTTPException(
            status_code=(r.status_code if r is not None else status.HTTP_404_NOT_FOUND),
            detail=detail if detail else "Pipeline not found",
        )
