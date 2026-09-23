import logging
import os
import time

import httpx
from fastapi import FastAPI

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("status-dashboard")

app = FastAPI(title="Status Dashboard")

# Comma-separated list of URLs to monitor, e.g. "https://github.com,https://example.com"
TARGETS = [t.strip() for t in os.getenv(
    "TARGETS", "https://github.com,https://example.com"
).split(",") if t.strip()]

TIMEOUT_SECONDS = float(os.getenv("TIMEOUT_SECONDS", "5"))


async def check_target(client: httpx.AsyncClient, url: str) -> dict:
    start = time.monotonic()
    try:
        response = await client.get(url, timeout=TIMEOUT_SECONDS, follow_redirects=True)
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        result = {
            "url": url,
            "up": response.status_code < 500,
            "status_code": response.status_code,
            "latency_ms": elapsed_ms,
        }
    except httpx.HTTPError as exc:
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        result = {
            "url": url,
            "up": False,
            "status_code": None,
            "latency_ms": elapsed_ms,
            "error": str(exc) or type(exc).__name__,
        }
    logger.info("checked target url=%s up=%s", url, result["up"])
    return result


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/status")
async def status():
    async with httpx.AsyncClient() as client:
        results = [await check_target(client, url) for url in TARGETS]
    return {
        "targets": results,
        "all_up": all(r["up"] for r in results),
    }
