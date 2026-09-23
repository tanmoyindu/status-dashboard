import respx
from fastapi.testclient import TestClient
from httpx import Response

from app.main import TARGETS, app

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@respx.mock
def test_status_all_up():
    for url in TARGETS:
        respx.get(url).mock(return_value=Response(200))

    response = client.get("/status")
    assert response.status_code == 200
    body = response.json()
    assert body["all_up"] is True
    assert len(body["targets"]) == len(TARGETS)
    assert all(t["up"] for t in body["targets"])


@respx.mock
def test_status_reports_down_target():
    urls = TARGETS
    respx.get(urls[0]).mock(return_value=Response(200))
    for url in urls[1:]:
        respx.get(url).mock(return_value=Response(503))

    response = client.get("/status")
    body = response.json()
    assert body["all_up"] is False
    assert body["targets"][0]["up"] is True
    assert body["targets"][1]["up"] is False


@respx.mock
def test_status_handles_connection_error():
    import httpx as httpx_module
    for url in TARGETS:
        respx.get(url).mock(side_effect=httpx_module.ConnectError("boom"))

    response = client.get("/status")
    body = response.json()
    assert body["all_up"] is False
    assert all(not t["up"] for t in body["targets"])
    assert "error" in body["targets"][0]
