import json

import httpx
import pytest
import respx
from typer.testing import CliRunner

from dida365_agent import cli, config

V1_BASE = "https://api.dida365.com/open/v1"
V2_BASE = "https://api.dida365.com/api/v2"

runner = CliRunner()

SAMPLE_TASK = {"id": "t1", "projectId": "p1", "title": "Test", "priority": 1, "status": 0}
SAMPLE_PROJECT = {"id": "p1", "name": "Inbox", "viewMode": "list", "kind": "TASK"}


@pytest.fixture
def configured(monkeypatch):
    """Configure V1 token + V2 session token, refresh both settings references."""
    monkeypatch.setenv("DIDA365_ACCESS_TOKEN", "test-token")
    monkeypatch.setenv("DIDA365_REGION", "china")
    monkeypatch.setenv("DIDA365_V2_SESSION_TOKEN", "v2-token")
    fresh = config.Settings()
    monkeypatch.setattr(config, "settings", fresh)
    monkeypatch.setattr(cli, "settings", fresh)
    return fresh


# ── V1 commands ──


@respx.mock
def test_project_list(configured):
    # Arrange
    respx.get(f"{V1_BASE}/project").mock(
        return_value=httpx.Response(200, json=[SAMPLE_PROJECT])
    )

    # Act
    result = runner.invoke(cli.app, ["project", "list"])

    # Assert
    assert result.exit_code == 0
    assert json.loads(result.stdout)[0]["name"] == "Inbox"


@respx.mock
def test_task_create(configured):
    # Arrange
    route = respx.post(f"{V1_BASE}/task").mock(
        return_value=httpx.Response(200, json=SAMPLE_TASK)
    )

    # Act
    result = runner.invoke(
        cli.app, ["task", "create", "--title", "Test", "--project", "p1"]
    )

    # Assert
    assert result.exit_code == 0
    assert route.called
    assert json.loads(result.stdout)["id"] == "t1"


# ── V2 command ──


@respx.mock
def test_search(configured):
    # Arrange
    respx.get(f"{V2_BASE}/search/all").mock(
        return_value=httpx.Response(200, json={"tasks": [SAMPLE_TASK]})
    )

    # Act
    result = runner.invoke(cli.app, ["search", "Test"])

    # Assert
    assert result.exit_code == 0
    assert json.loads(result.stdout)["tasks"][0]["id"] == "t1"


@respx.mock
def test_column_list(configured):
    # Arrange
    respx.get(f"{V2_BASE}/column/project/p1").mock(
        return_value=httpx.Response(
            200, json=[{"id": "c1", "projectId": "p1", "name": "Backlog"}]
        )
    )

    # Act
    result = runner.invoke(cli.app, ["column", "list", "p1"])

    # Assert
    assert result.exit_code == 0
    assert json.loads(result.stdout)[0]["name"] == "Backlog"


@respx.mock
def test_column_create(configured):
    # Arrange
    route = respx.post(f"{V2_BASE}/column").mock(
        return_value=httpx.Response(200, json={"id2etag": {"c1": "etag"}})
    )

    # Act
    result = runner.invoke(
        cli.app, ["column", "create", "--project", "p1", "--name", "Todo"]
    )

    # Assert
    assert result.exit_code == 0
    assert route.called
    sent = json.loads(route.calls.last.request.content)
    assert sent["add"][0] == {"projectId": "p1", "name": "Todo"}


# ── Error path ──


@respx.mock
def test_error_to_stderr_nonzero_exit(configured):
    # Arrange
    respx.get(f"{V1_BASE}/project/bad").mock(
        return_value=httpx.Response(404, text="not found")
    )

    # Act
    result = runner.invoke(cli.app, ["project", "get", "bad"])

    # Assert
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "Error" in result.stderr


# ── Auth status ──


def test_auth_status_no_token(monkeypatch, tmp_path):
    # Arrange: no env token, point token file at empty tmp location
    monkeypatch.delenv("DIDA365_ACCESS_TOKEN", raising=False)
    fresh = config.Settings(dida365_access_token="")
    monkeypatch.setattr(config, "settings", fresh)
    monkeypatch.setattr(cli, "settings", fresh)
    from dida365_agent import auth

    monkeypatch.setattr(auth, "TOKEN_FILE", tmp_path / "token.json")

    # Act
    result = runner.invoke(cli.app, ["auth", "status"])

    # Assert
    assert result.exit_code == 1
    assert "No token" in result.stderr


def test_auth_status_from_env(monkeypatch):
    # Arrange
    monkeypatch.setenv("DIDA365_ACCESS_TOKEN", "env-token")
    fresh = config.Settings()
    monkeypatch.setattr(config, "settings", fresh)
    monkeypatch.setattr(cli, "settings", fresh)

    # Act
    result = runner.invoke(cli.app, ["auth", "status"])

    # Assert
    assert result.exit_code == 0
    assert json.loads(result.stdout)["source"] == "env"
