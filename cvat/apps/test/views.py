# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from django.db.models import Count
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cvat.apps.engine.models import LabeledShape, Task
from cvat.apps.engine.permissions import TaskPermission


class TaskAnnotationCountsView(APIView):
    """Return the number of saved labeled shapes per label for a task."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="get_task_annotation_counts",
        summary="Get annotation counts by label for a task",
        responses={200: dict},
    )
    def get(self, request, task_id: int):
        task = get_object_or_404(Task, pk=task_id)
        permission = TaskPermission.create_scope_view(request, task)
        if not permission.check_access().allow:
            raise PermissionDenied("You do not have permission to view this task")

        counts = (
            LabeledShape.objects.filter(job__segment__task=task)
            .values("label_id", "label__name")
            .annotate(count=Count("id"))
            .order_by("label__name", "label_id")
        )

        return Response(
            {
                "task_id": task.id,
                "counts": [
                    {"label_id": row["label_id"], "label": row["label__name"], "count": row["count"]}
                    for row in counts
                ],
            }
        )
