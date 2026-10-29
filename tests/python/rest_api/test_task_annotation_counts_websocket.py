# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

import asyncio

from cvat.apps.test import websocket as websocket_module


def test_annotation_counts_websocket_path_accepts_a_task_id():
    match = websocket_module._TASK_COUNTS_PATH.fullmatch("/ws/tasks/42/annotation-counts")

    assert match
    assert match["task_id"] == "42"


def test_annotation_counts_websocket_path_rejects_other_routes():
    assert websocket_module._TASK_COUNTS_PATH.fullmatch("/api/tasks/42/annotation-counts") is None


def test_annotation_counts_websocket_keeps_connection_alive_while_idle(monkeypatch):
    calls = {"count": 0}
    sent_messages = []

    def fake_sync_to_async(func, thread_sensitive=True):
        async def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    async def fake_receive():
        calls["count"] += 1
        if calls["count"] == 1:
            raise TimeoutError
        return {"type": "websocket.disconnect"}

    async def fake_send(message):
        sent_messages.append(message)

    monkeypatch.setattr(websocket_module, "sync_to_async", fake_sync_to_async)
    monkeypatch.setattr(websocket_module, "_can_view_task", lambda scope, task_id: True)
    monkeypatch.setattr(websocket_module, "_counts_signature", lambda task_id: ((1, "manual", 2),))

    asyncio.run(
        websocket_module.annotation_counts_ws(
            {"type": "websocket", "path": "/ws/tasks/42/annotation-counts", "headers": []},
            fake_receive,
            fake_send,
        ),
    )

    assert any(message.get("type") == "websocket.accept" for message in sent_messages)
    assert any(
        message.get("type") == "websocket.send" and message.get("text") == '{"type": "ping"}'
        for message in sent_messages
    )
