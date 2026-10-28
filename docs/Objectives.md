# Annotation Analytics Objectives

**Base CVAT commit:** `a81ed252dce15b805d5a544116cf98005e42f257`

| ID | What is measured | How | Target | Conditions / exclusions |
| --- | --- | --- | --- | --- |
| MO-1 | Server response time for `GET /api/tasks/{task_id}/annotation-counts` | Five timed HTTP requests against the local Docker CVAT stack; preserve each raw duration, then report median and spread. | Median at or below 200 ms. This is a first target for a small aggregate endpoint, to be evaluated against the actual sample task and machine. | Record CPU, RAM, OS, task/image count, and base CVAT commit before reporting. Exclude the first request after startup and state that exclusion. No measurements recorded yet. |

## Measurement record

Pending endpoint implementation and a running local stack. Add the five raw durations and environment details here; do not claim the target is met without them.
