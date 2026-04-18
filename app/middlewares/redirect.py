from fastapi import Request
from starlette.responses import RedirectResponse


async def enforce_slash_middleware(request: Request, call_next):
    path = request.url.path

    if (
        path != "/"
        and not path.endswith("/")
        and not path.startswith(("/docs", "/openapi"))
    ):
        query_params = f"?{request.url.query}" if request.url.query else ""
        return RedirectResponse(url=f"{path}/{query_params}", status_code=301)
    return await call_next(request)
