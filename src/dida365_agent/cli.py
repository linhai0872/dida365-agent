"""CLI for Dida365/TickTick — agent-friendly, JSON output by default.

Business logic is reused from client.py (V1) and client_v2.py (V2).
Every command prints JSON to stdout; errors go to stderr with a non-zero exit.
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

import typer

from . import auth
from .client import Dida365Client
from .client_v2 import Dida365V2Client, resolve_v2_token
from .config import settings

app = typer.Typer(
    help="Manage Dida365/TickTick tasks from the terminal. JSON output by default.",
    no_args_is_help=True,
)
task_app = typer.Typer(help="Task operations.", no_args_is_help=True)
project_app = typer.Typer(help="Project operations.", no_args_is_help=True)
tag_app = typer.Typer(help="Tag operations (V2).", no_args_is_help=True)
habit_app = typer.Typer(help="Habit operations (V2).", no_args_is_help=True)
folder_app = typer.Typer(help="Project folder operations (V2).", no_args_is_help=True)
auth_app = typer.Typer(help="Authentication.", no_args_is_help=True)

app.add_typer(task_app, name="task")
app.add_typer(project_app, name="project")
app.add_typer(tag_app, name="tag")
app.add_typer(habit_app, name="habit")
app.add_typer(folder_app, name="folder")
app.add_typer(auth_app, name="auth")


# ── Shared helpers ──

_FIELD_MAP = {
    "project_id": "projectId",
    "start_date": "startDate",
    "due_date": "dueDate",
    "is_all_day": "isAllDay",
    "time_zone": "timeZone",
    "repeat_flag": "repeatFlag",
    "view_mode": "viewMode",
    "sort_order": "sortOrder",
    "task_id": "id",
}


def _build_data(**kwargs: Any) -> dict[str, Any]:
    return {_FIELD_MAP.get(k, k): v for k, v in kwargs.items() if v is not None}


def _dump(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump(exclude_none=True)
    if isinstance(obj, list):
        return [_dump(i) for i in obj]
    return obj


def _output(obj: Any) -> None:
    print(json.dumps(_dump(obj), ensure_ascii=False, indent=2))


def _fail(e: Exception) -> None:
    import httpx

    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        hints = {
            401: "Unauthorized — token may have expired. Run: dida auth login",
            403: "Forbidden — token lacks permission for this operation.",
            404: "Not found — verify the project_id / task_id via a list command.",
            429: "Rate limited — wait 30-60s before retrying.",
        }
        msg = hints.get(status, f"API error (HTTP {status})")
        print(f"Error: {msg}\nDetails: {e.response.text}", file=sys.stderr)
    elif isinstance(e, httpx.TimeoutException):
        print("Error: Request timed out. Check connectivity and retry.", file=sys.stderr)
    else:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
    raise typer.Exit(1)


def _run_v1(coro_fn) -> None:
    """Run an async fn(client) against a V1 client, output result, close client."""

    async def _wrap() -> Any:
        client = Dida365Client()
        try:
            return await coro_fn(client)
        finally:
            await client.close()

    try:
        result = asyncio.run(_wrap())
    except Exception as e:  # noqa: BLE001
        _fail(e)
        return
    if result is not None:
        _output(result)


def _run_v2(coro_fn) -> None:
    """Resolve V2 token, run an async fn(client), output result, close client."""

    async def _wrap() -> Any:
        token = await resolve_v2_token(settings)
        if not token:
            raise RuntimeError(
                "V2 not configured. Set DIDA365_V2_SESSION_TOKEN "
                "(browser DevTools → Application → Cookies → copy 't' value), "
                "or DIDA365_USERNAME + DIDA365_PASSWORD (no 2FA) in .env."
            )
        client = Dida365V2Client(session_token=token, base_url=settings.v2_api_base_url)
        try:
            return await coro_fn(client)
        finally:
            await client.close()

    try:
        result = asyncio.run(_wrap())
    except Exception as e:  # noqa: BLE001
        _fail(e)
        return
    if result is not None:
        _output(result)


def _load_json_arg(json_str: str | None, file: Path | None) -> Any:
    if json_str is not None:
        return json.loads(json_str)
    if file is not None:
        return json.loads(file.read_text(encoding="utf-8"))
    print("Error: provide --json '<JSON>' or --file <path>.", file=sys.stderr)
    raise typer.Exit(1)


# ── Task commands ──


@task_app.command("create")
def task_create(
    title: str = typer.Option(..., "--title"),
    project: str = typer.Option(..., "--project", help="Project ID"),
    content: str | None = typer.Option(None, "--content"),
    desc: str | None = typer.Option(None, "--desc"),
    start_date: str | None = typer.Option(None, "--start-date"),
    due_date: str | None = typer.Option(None, "--due-date"),
    priority: int | None = typer.Option(None, "--priority", help="0=None,1=Low,3=Medium,5=High"),
    tags: str | None = typer.Option(None, "--tags", help="Comma-separated tag names"),
    is_all_day: bool | None = typer.Option(None, "--all-day/--no-all-day"),
    time_zone: str | None = typer.Option(None, "--time-zone"),
    reminders: str | None = typer.Option(None, "--reminders", help="Comma-separated triggers"),
    repeat_flag: str | None = typer.Option(None, "--repeat-flag", help="RRULE; needs start-date"),
    kind: str | None = typer.Option(None, "--kind", help="TEXT, NOTE, or CHECKLIST"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
) -> None:
    """Create a task."""
    data = _build_data(
        title=title,
        project_id=project,
        content=content,
        desc=desc,
        start_date=start_date,
        due_date=due_date,
        priority=priority,
        tags=tags.split(",") if tags else None,
        is_all_day=is_all_day,
        time_zone=time_zone,
        reminders=reminders.split(",") if reminders else None,
        repeat_flag=repeat_flag,
        kind=kind,
        sort_order=sort_order,
    )
    _run_v1(lambda c: c.create_task(data))


@task_app.command("update")
def task_update(
    task_id: str = typer.Argument(..., help="Task ID"),
    project: str = typer.Option(..., "--project", help="Project ID"),
    title: str | None = typer.Option(None, "--title"),
    content: str | None = typer.Option(None, "--content"),
    desc: str | None = typer.Option(None, "--desc"),
    start_date: str | None = typer.Option(None, "--start-date"),
    due_date: str | None = typer.Option(None, "--due-date"),
    priority: int | None = typer.Option(None, "--priority"),
    tags: str | None = typer.Option(None, "--tags", help="Comma-separated tag names"),
    is_all_day: bool | None = typer.Option(None, "--all-day/--no-all-day"),
    time_zone: str | None = typer.Option(None, "--time-zone"),
    reminders: str | None = typer.Option(None, "--reminders"),
    repeat_flag: str | None = typer.Option(None, "--repeat-flag"),
    kind: str | None = typer.Option(None, "--kind"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
) -> None:
    """Update a task. Only provided fields change."""
    data = _build_data(
        task_id=task_id,
        project_id=project,
        title=title,
        content=content,
        desc=desc,
        start_date=start_date,
        due_date=due_date,
        priority=priority,
        tags=tags.split(",") if tags else None,
        is_all_day=is_all_day,
        time_zone=time_zone,
        reminders=reminders.split(",") if reminders else None,
        repeat_flag=repeat_flag,
        kind=kind,
        sort_order=sort_order,
    )
    _run_v1(lambda c: c.update_task(task_id, data))


@task_app.command("get")
def task_get(
    project: str = typer.Argument(..., help="Project ID"),
    task_id: str = typer.Argument(..., help="Task ID"),
) -> None:
    """Get a task by project ID and task ID."""
    _run_v1(lambda c: c.get_task(project, task_id))


@task_app.command("get-by-id")
def task_get_by_id(task_id: str = typer.Argument(..., help="Task ID")) -> None:
    """Get a task by ID only (no project ID needed)."""
    _run_v1(lambda c: c.get_task_by_id(task_id))


@task_app.command("complete")
def task_complete(
    project: str = typer.Argument(..., help="Project ID"),
    task_id: str = typer.Argument(..., help="Task ID"),
) -> None:
    """Mark a task as completed."""

    async def _do(c: Dida365Client) -> dict:
        await c.complete_task(project, task_id)
        return {"completed": task_id}

    _run_v1(_do)


@task_app.command("delete")
def task_delete(
    project: str = typer.Argument(..., help="Project ID"),
    task_id: str = typer.Argument(..., help="Task ID"),
) -> None:
    """Permanently delete a task."""

    async def _do(c: Dida365Client) -> dict:
        await c.delete_task(project, task_id)
        return {"deleted": task_id}

    _run_v1(_do)


@task_app.command("move")
def task_move(
    task_id: str = typer.Option(..., "--task", help="Task ID"),
    from_project: str = typer.Option(..., "--from", help="Source project ID"),
    to_project: str = typer.Option(..., "--to", help="Destination project ID"),
) -> None:
    """Move a task between projects."""
    _run_v1(lambda c: c.move_task(task_id, from_project, to_project))


@task_app.command("completed")
def task_completed(
    projects: str | None = typer.Option(None, "--projects", help="Comma-separated project IDs"),
    start_date: str | None = typer.Option(None, "--start-date"),
    end_date: str | None = typer.Option(None, "--end-date"),
) -> None:
    """List completed tasks within an optional time range."""
    _run_v1(
        lambda c: c.list_completed_tasks(
            project_ids=projects.split(",") if projects else None,
            start_date=start_date,
            end_date=end_date,
        )
    )


@task_app.command("filter")
def task_filter(
    projects: str | None = typer.Option(None, "--projects", help="Comma-separated project IDs"),
    start_date: str | None = typer.Option(None, "--start-date"),
    end_date: str | None = typer.Option(None, "--end-date"),
    priority: str | None = typer.Option(None, "--priority", help="Comma-separated: 0,1,3,5"),
    tags: str | None = typer.Option(None, "--tags", help="Comma-separated tag names (AND)"),
    status: str | None = typer.Option(None, "--status", help="Comma-separated: 0=normal,2=done"),
) -> None:
    """Filter tasks across projects."""
    _run_v1(
        lambda c: c.filter_tasks(
            project_ids=projects.split(",") if projects else None,
            start_date=start_date,
            end_date=end_date,
            priority=[int(p) for p in priority.split(",")] if priority else None,
            tags=tags.split(",") if tags else None,
            status=[int(s) for s in status.split(",")] if status else None,
        )
    )


@task_app.command("undone")
def task_undone(
    projects: str | None = typer.Option(None, "--projects", help="Comma-separated project IDs"),
    start_date: str | None = typer.Option(None, "--start-date"),
    end_date: str | None = typer.Option(None, "--end-date"),
) -> None:
    """List undone tasks within a date range."""
    _run_v1(
        lambda c: c.list_undone_tasks(
            start_date=start_date,
            end_date=end_date,
            project_ids=projects.split(",") if projects else None,
        )
    )


@task_app.command("batch-create")
def task_batch_create(
    json_str: str | None = typer.Option(None, "--json", help="JSON array of tasks"),
    file: Path | None = typer.Option(None, "--file", help="Path to JSON array file"),
) -> None:
    """Batch create tasks. Each item needs title and projectId."""
    tasks = _load_json_arg(json_str, file)
    _run_v1(lambda c: c.batch_create_tasks(tasks))


@task_app.command("batch-update")
def task_batch_update(
    json_str: str | None = typer.Option(None, "--json", help="JSON array of tasks"),
    file: Path | None = typer.Option(None, "--file", help="Path to JSON array file"),
) -> None:
    """Batch update tasks. Each item needs id and projectId."""
    tasks = _load_json_arg(json_str, file)
    _run_v1(lambda c: c.batch_update_tasks(tasks))


@task_app.command("batch-complete")
def task_batch_complete(
    project: str = typer.Option(..., "--project", help="Project ID"),
    task_ids: str = typer.Option(..., "--tasks", help="Comma-separated task IDs"),
) -> None:
    """Mark multiple tasks in a project as completed."""
    ids = task_ids.split(",")

    async def _do(c: Dida365Client) -> dict:
        await c.batch_complete_tasks(project, ids)
        return {"completed": ids}

    _run_v1(_do)


@task_app.command("set-parent")
def task_set_parent(
    task_id: str = typer.Argument(..., help="Child task ID"),
    parent_id: str = typer.Argument(..., help="Parent task ID"),
) -> None:
    """Set a task's parent (V2)."""
    _run_v2(lambda c: c.set_task_parent(task_id, parent_id))


@task_app.command("unset-parent")
def task_unset_parent(task_id: str = typer.Argument(..., help="Task ID")) -> None:
    """Remove a task's parent, making it top-level (V2)."""
    _run_v2(lambda c: c.unset_task_parent(task_id))


@task_app.command("pin")
def task_pin(
    task_id: str = typer.Argument(..., help="Task ID"),
    pinned: bool = typer.Option(True, "--pinned/--unpinned"),
) -> None:
    """Pin or unpin a task (V2)."""
    _run_v2(lambda c: c.pin_task(task_id, pinned))


# ── Project commands ──


@project_app.command("list")
def project_list() -> None:
    """List all projects."""
    _run_v1(lambda c: c.list_projects())


@project_app.command("get")
def project_get(project_id: str = typer.Argument(..., help="Project ID")) -> None:
    """Get project details."""
    _run_v1(lambda c: c.get_project(project_id))


@project_app.command("data")
def project_data(project_id: str = typer.Argument(..., help="Project ID")) -> None:
    """Get a project with its tasks and columns."""
    _run_v1(lambda c: c.get_project_with_data(project_id))


@project_app.command("create")
def project_create(
    name: str = typer.Option(..., "--name"),
    color: str | None = typer.Option(None, "--color"),
    view_mode: str | None = typer.Option(None, "--view-mode", help="list|kanban|timeline"),
    kind: str | None = typer.Option(None, "--kind", help="TASK|NOTE"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
) -> None:
    """Create a project."""
    data = _build_data(
        name=name, color=color, view_mode=view_mode, kind=kind, sort_order=sort_order
    )
    _run_v1(lambda c: c.create_project(data))


@project_app.command("update")
def project_update(
    project_id: str = typer.Argument(..., help="Project ID"),
    name: str | None = typer.Option(None, "--name"),
    color: str | None = typer.Option(None, "--color"),
    view_mode: str | None = typer.Option(None, "--view-mode"),
    kind: str | None = typer.Option(None, "--kind"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
) -> None:
    """Update a project. Only provided fields change."""
    data = _build_data(
        name=name, color=color, view_mode=view_mode, kind=kind, sort_order=sort_order
    )
    _run_v1(lambda c: c.update_project(project_id, data))


@project_app.command("delete")
def project_delete(project_id: str = typer.Argument(..., help="Project ID")) -> None:
    """Permanently delete a project and all its tasks."""

    async def _do(c: Dida365Client) -> dict:
        await c.delete_project(project_id)
        return {"deleted": project_id}

    _run_v1(_do)


# ── Search (V2, top-level) ──


@app.command("search")
def search(
    keywords: str = typer.Argument(..., help="Search query"),
    projects: str | None = typer.Option(None, "--projects", help="Comma-separated project IDs"),
    tags: str | None = typer.Option(None, "--tags", help="Comma-separated tag names"),
    status: str | None = typer.Option(None, "--status", help="Comma-separated: 0=active,2=done"),
    due_from: int | None = typer.Option(None, "--due-from", help="ms timestamp"),
    due_to: int | None = typer.Option(None, "--due-to", help="ms timestamp"),
) -> None:
    """Server-side full-text search for tasks (V2)."""
    _run_v2(
        lambda c: c.search_tasks(
            keywords,
            project_ids=projects.split(",") if projects else None,
            tags=tags.split(",") if tags else None,
            statuses=[int(s) for s in status.split(",")] if status else None,
            due_from=due_from,
            due_to=due_to,
        )
    )


# ── Tag commands (V2) ──


@tag_app.command("list")
def tag_list() -> None:
    """List all tags (V2)."""
    _run_v2(lambda c: c.list_tags())


@tag_app.command("create")
def tag_create(
    json_str: str | None = typer.Option(None, "--json", help="JSON array of tags"),
    file: Path | None = typer.Option(None, "--file", help="Path to JSON array file"),
) -> None:
    """Batch create tags. Each item needs name (V2)."""
    tags = _load_json_arg(json_str, file)
    _run_v2(lambda c: c.create_tags(tags))


@tag_app.command("update")
def tag_update(
    json_str: str | None = typer.Option(None, "--json", help="JSON array of tags"),
    file: Path | None = typer.Option(None, "--file", help="Path to JSON array file"),
) -> None:
    """Batch update tags. Each item needs name (V2)."""
    tags = _load_json_arg(json_str, file)
    _run_v2(lambda c: c.update_tags(tags))


@tag_app.command("delete-batch")
def tag_delete_batch(
    json_str: str | None = typer.Option(None, "--json", help="JSON array of tags"),
    file: Path | None = typer.Option(None, "--file", help="Path to JSON array file"),
) -> None:
    """Batch delete tags. Each item needs name (V2)."""
    tags = _load_json_arg(json_str, file)
    _run_v2(lambda c: c.delete_tags(tags))


@tag_app.command("delete")
def tag_delete(name: str = typer.Argument(..., help="Tag name")) -> None:
    """Delete a single tag by name (V2)."""

    async def _do(c: Dida365V2Client) -> dict:
        await c.delete_tag(name)
        return {"deleted": name}

    _run_v2(_do)


# ── Habit commands (V2) ──


@habit_app.command("list")
def habit_list() -> None:
    """List all habits (V2)."""
    _run_v2(lambda c: c.list_habits())


@habit_app.command("create")
def habit_create(
    json_str: str | None = typer.Option(None, "--json", help="JSON array of habits"),
    file: Path | None = typer.Option(None, "--file", help="Path to JSON array file"),
) -> None:
    """Batch create habits. Each item needs name (V2)."""
    habits = _load_json_arg(json_str, file)
    _run_v2(lambda c: c.create_habit(habits))


@habit_app.command("update")
def habit_update(
    json_str: str | None = typer.Option(None, "--json", help="JSON array of habits"),
    file: Path | None = typer.Option(None, "--file", help="Path to JSON array file"),
) -> None:
    """Batch update habits. Each item needs id (V2)."""
    habits = _load_json_arg(json_str, file)
    _run_v2(lambda c: c.update_habit(habits))


@habit_app.command("delete")
def habit_delete(
    json_str: str | None = typer.Option(None, "--json", help="JSON array of habits"),
    file: Path | None = typer.Option(None, "--file", help="Path to JSON array file"),
) -> None:
    """Batch delete habits. Each item needs id (V2)."""
    habits = _load_json_arg(json_str, file)
    _run_v2(lambda c: c.delete_habit(habits))


@habit_app.command("checkin")
def habit_checkin(
    habit_id: str = typer.Argument(..., help="Habit ID"),
    checkin_stamp: str = typer.Argument(..., help="Date stamp YYYYMMDD"),
    status: int = typer.Option(2, "--status", help="0=unchecked,2=checked"),
    value: float | None = typer.Option(None, "--value"),
    goal: int | None = typer.Option(None, "--goal"),
) -> None:
    """Check in a habit for a date (V2)."""
    data: dict[str, Any] = {
        "habitId": habit_id,
        "checkinStamp": checkin_stamp,
        "status": status,
    }
    if value is not None:
        data["value"] = value
    if goal is not None:
        data["goal"] = goal
    _run_v2(lambda c: c.checkin_habit(data))


@habit_app.command("undo-checkin")
def habit_undo_checkin(
    habit_id: str = typer.Argument(..., help="Habit ID"),
    checkin_stamp: str = typer.Argument(..., help="Date stamp YYYYMMDD"),
) -> None:
    """Undo a habit checkin for a date (V2)."""

    async def _do(c: Dida365V2Client) -> dict:
        await c.undo_checkin(habit_id, checkin_stamp)
        return {"undone": {"habitId": habit_id, "stamp": checkin_stamp}}

    _run_v2(_do)


@habit_app.command("checkins")
def habit_checkins(
    habit_id: str = typer.Argument(..., help="Habit ID"),
    after_stamp: str | None = typer.Option(None, "--after", help="Only after this stamp YYYYMMDD"),
) -> None:
    """List checkin records for a habit (V2)."""
    _run_v2(lambda c: c.list_habit_checkins(habit_id, after_stamp))


@habit_app.command("sections")
def habit_sections() -> None:
    """List habit sections/groups (V2)."""
    _run_v2(lambda c: c.list_habit_sections())


# ── Folder commands (V2) ──


@folder_app.command("list")
def folder_list() -> None:
    """List all project folders (V2)."""
    _run_v2(lambda c: c.list_folders())


@folder_app.command("create")
def folder_create(
    name: str = typer.Option(..., "--name"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
) -> None:
    """Create a project folder (V2)."""
    data: dict[str, Any] = {"name": name}
    if sort_order is not None:
        data["sortOrder"] = sort_order
    _run_v2(lambda c: c.create_folder(data))


@folder_app.command("update")
def folder_update(
    folder_id: str = typer.Argument(..., help="Folder ID"),
    name: str | None = typer.Option(None, "--name"),
    sort_order: int | None = typer.Option(None, "--sort-order"),
) -> None:
    """Update a project folder. Only provided fields change (V2)."""
    data: dict[str, Any] = {}
    if name is not None:
        data["name"] = name
    if sort_order is not None:
        data["sortOrder"] = sort_order
    _run_v2(lambda c: c.update_folder(folder_id, data))


@folder_app.command("delete")
def folder_delete(folder_id: str = typer.Argument(..., help="Folder ID")) -> None:
    """Delete a project folder (V2). Projects inside are not deleted."""

    async def _do(c: Dida365V2Client) -> dict:
        await c.delete_folder(folder_id)
        return {"deleted": folder_id}

    _run_v2(_do)


# ── Auth commands ──


@auth_app.command("login")
def auth_login() -> None:
    """Browser OAuth login (opens browser, saves token ~180 days)."""
    from . import _oauth_flow

    _oauth_flow.main()


@auth_app.command("status")
def auth_status() -> None:
    """Show current token status."""
    if settings.dida365_access_token:
        _output({"source": "env", "configured": True})
        return
    token_data = auth._load_token()
    if not token_data or not token_data.get("access_token"):
        print("Error: No token found. Run: dida auth login", file=sys.stderr)
        raise typer.Exit(1)
    tok = token_data["access_token"]
    out: dict[str, Any] = {"source": "file", "token_prefix": tok[:16] + "..."}
    obtained_at = token_data.get("obtained_at")
    expires_in = token_data.get("expires_in")
    if obtained_at and expires_in:
        remaining = obtained_at + expires_in - int(time.time())
        out["expired"] = auth._is_token_expired(token_data)
        out["remaining_days"] = max(0, remaining // 86400)
    _output(out)


@auth_app.command("logout")
def auth_logout() -> None:
    """Remove the locally stored token."""
    if auth.TOKEN_FILE.exists():
        auth.TOKEN_FILE.unlink()
        _output({"logout": True})
    else:
        _output({"logout": True, "note": "no token file"})


@auth_app.command("token")
def auth_token(
    access_token: str = typer.Argument(..., help="Access token to store"),
    expires_in: int = typer.Option(
        15552000, "--expires-in", help="Validity in seconds (default ~180 days)"
    ),
) -> None:
    """Store an access token directly (skip browser OAuth)."""
    auth._save_token(
        {
            "access_token": access_token,
            "obtained_at": int(time.time()),
            "expires_in": expires_in,
        }
    )
    _output({"saved": True, "token_prefix": access_token[:16] + "..."})


if __name__ == "__main__":
    app()
