# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from django.urls import path

from .views import TaskAnnotationCountsView

app_name = "test"

urlpatterns = [
    path(
        "api/tasks/<int:task_id>/annotation-counts",
        TaskAnnotationCountsView.as_view(),
        name="task-annotation-counts",
    ),
]
