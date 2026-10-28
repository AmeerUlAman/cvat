# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

from django.db.models import Count
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cvat.apps.engine.models import LabeledShape, SourceType, Task
from cvat.apps.engine.permissions import TaskPermission


class TaskAnnotationCountsView(APIView):
    """Return the number of saved labeled shapes per label for a task."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="get_task_annotation_counts",
        summary="Get annotation counts by label for a task",
        parameters=[
            OpenApiParameter(
                "source",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Only count annotations from this source",
                enum=[str(source) for source in SourceType],
            ),
        ],
        responses={200: dict},
    )
    def get(self, request, task_id: int):
        task = get_object_or_404(Task, pk=task_id)
        permission = TaskPermission.create_scope_view(request, task)
        if not permission.check_access().allow:
            raise PermissionDenied("You do not have permission to view this task")

        source = request.query_params.get("source")
        if source and source not in {str(candidate) for candidate in SourceType}:
            raise ValidationError({"source": f"Unsupported annotation source: {source}"})

        shapes = LabeledShape.objects.filter(job__segment__task=task)
        if source:
            shapes = shapes.filter(source=source)

        counts = (
            shapes.values("label_id", "label__name")
            .annotate(count=Count("id"))
            .order_by("label__name", "label_id")
        )

        return Response(
            {
                "task_id": task.id,
                "source": source,
                "counts": [
                    {"label_id": row["label_id"], "label": row["label__name"], "count": row["count"]}
                    for row in counts
                ],
            }
        )
