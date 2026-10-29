# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import importlib
import json
import re
from http.cookies import SimpleCookie
from typing import Any

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user
from django.db.models import Count
from django.test import RequestFactory

from cvat.apps.engine.models import LabeledShape, Task
from cvat.apps.engine.permissions import TaskPermission
from cvat.apps.iam.middleware import get_organization


_TASK_COUNTS_PATH = re.compile(r"^/ws/tasks/(?P<task_id>\d+)/annotation-counts/?$")
_CHECK_INTERVAL_SECONDS = 1.5
_PING_INTERVAL_SECONDS = 20
_PING_MESSAGE = json.dumps({"type": "ping"})


def _session_key_from_scope(scope: dict[str, Any]) -> str | None:
    cookies = SimpleCookie()
    for name, value in scope.get("headers", []):
        if name.lower() == b"cookie":
            cookies.load(value.decode("latin-1"))

    session_cookie = cookies.get(settings.SESSION_COOKIE_NAME)
    return session_cookie.value if session_cookie else None


def _can_view_task(scope: dict[str, Any], task_id: int) -> bool:
    session_key = _session_key_from_scope(scope)
    if not session_key:
        return False

    SessionStore = importlib.import_module(settings.SESSION_ENGINE).SessionStore
    request = RequestFactory().get(scope["path"])
    request.session = SessionStore(session_key=session_key)
    request.user = get_user(request)
    if not request.user.is_authenticated:
        return False

    try:
        task = Task.objects.select_related("organization").get(pk=task_id)
    except Task.DoesNotExist:
        return False

    request.iam_context = get_organization(request)
    return TaskPermission.create_scope_view(request, task).check_access().allow


def _counts_signature(task_id: int) -> tuple[tuple[int, str | None, int], ...]:
    """Return the dimensions that change the graph's visible values."""
    rows = (
        LabeledShape.objects.filter(job__segment__task_id=task_id)
        .values("label_id", "source")
        .annotate(count=Count("id"))
        .order_by("label_id", "source")
    )
    return tuple((row["label_id"], row["source"], row["count"]) for row in rows)


async def annotation_counts_ws(scope, receive, send):
    """Notify authorized clients when saved-shape counts change for a task.

    The comparison uses the database because CVAT saves imports in bulk, bypassing
    Django model signals. It therefore works across separate server processes too.
    """
    if scope.get("type") != "websocket":
        return

    match = _TASK_COUNTS_PATH.fullmatch(scope.get("path", ""))
    if not match:
        await send({"type": "websocket.close", "code": 4404})
        return

    task_id = int(match["task_id"])
    if not await sync_to_async(_can_view_task, thread_sensitive=True)(scope, task_id):
        await send({"type": "websocket.close", "code": 4403})
        return

    await send({"type": "websocket.accept"})
    signature = await sync_to_async(_counts_signature, thread_sensitive=True)(task_id)
    last_ping_at = asyncio.get_running_loop().time()

    while True:
        try:
            message = await asyncio.wait_for(receive(), timeout=_CHECK_INTERVAL_SECONDS)
        except TimeoutError:
            current_time = asyncio.get_running_loop().time()
            current_signature = await sync_to_async(_counts_signature, thread_sensitive=True)(task_id)
            if current_time - last_ping_at >= _PING_INTERVAL_SECONDS:
                await send({"type": "websocket.send", "text": _PING_MESSAGE})
                last_ping_at = current_time
            if current_signature != signature:
                signature = current_signature
                await send(
                    {
                        "type": "websocket.send",
                        "text": json.dumps(
                            {"type": "annotation_counts_updated", "task_id": task_id}
                        ),
                    }
                )
            continue

        if message["type"] == "websocket.disconnect":
            return

        if message.get("type") == "websocket.receive":
            continue
