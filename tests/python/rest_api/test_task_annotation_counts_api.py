# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from cvat.apps.test.views import TaskAnnotationCountsView


def test_task_annotation_counts_view_uses_collection_permission_shape():
    assert TaskAnnotationCountsView.detail is False
