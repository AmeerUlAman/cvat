# Annotation Analytics Objectives

**Base CVAT commit:** `a81ed252dce15b805d5a544116cf98005e42f257`

| ID | What is measured | How | Target | Conditions / exclusions |
| --- | --- | --- | --- | --- |
| MO-1 | Server response time for `GET /api/tasks/{task_id}/annotation-counts` | Five timed HTTP requests against the local Docker CVAT stack; preserve each raw duration, then report median and spread. | Median at or below 200 ms. This is a first target for a small aggregate endpoint, to be evaluated against the actual sample task and machine. | Record CPU, RAM, OS, task/image count, and base CVAT commit before reporting. Exclude the first request after startup and state that exclusion. |

## MO-1 measurement record

Measured 29 October 2026 against task 14 through the local Docker stack's HTTP entry point. The first request after restarting the backend was a warm-up and was excluded as planned. Each response was HTTP 200 and contained 80 label groups.

```text
warm-up (excluded): status=200 groups=80 duration_ms=162.775
run 1: status=200 groups=80 duration_ms=127.095
run 2: status=200 groups=80 duration_ms=149.311
run 3: status=200 groups=80 duration_ms=120.987
run 4: status=200 groups=80 duration_ms=140.851
run 5: status=200 groups=80 duration_ms=131.887
median_ms=131.887
spread_ms=28.324 (min=120.987, max=149.311)
```

The 131.887 ms median meets the target of at most 200 ms.

Environment: Intel Core i7-6820HQ at 2.70 GHz; 17,053,630,464 bytes (15.88 GiB) physical RAM; Microsoft Windows 11 Pro 10.0.26100; Docker-based local CVAT stack; task 14 with 5,000 images and 41,869 saved shapes; base CVAT SHA `a81ed252dce15b805d5a544116cf98005e42f257`.
