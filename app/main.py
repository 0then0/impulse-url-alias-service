from fastapi import FastAPI

from app.api.v1 import private, public

app = FastAPI(
    title="URL Alias Service",
    description="A service for shortening URLs, managing them and collecting statistics.",
    version="1.0.0",
)


@app.get("/ping", summary="Checking service availability")
async def ping():
    return {"pong": "ok"}


app.include_router(public.router, prefix="", tags=["public"])
app.include_router(private.router, prefix="/api/v1", tags=["private"])
