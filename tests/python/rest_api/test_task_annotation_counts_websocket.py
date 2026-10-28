# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from cvat.apps.test.websocket import _TASK_COUNTS_PATH


def test_annotation_counts_websocket_path_accepts_a_task_id():
    match = _TASK_COUNTS_PATH.fullmatch("/ws/tasks/42/annotation-counts")

    assert match
    assert match["task_id"] == "42"


def test_annotation_counts_websocket_path_rejects_other_routes():
    assert _TASK_COUNTS_PATH.fullmatch("/api/tasks/42/annotation-counts") is None
