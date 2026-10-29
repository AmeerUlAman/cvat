# Annotation Analytics Plan

**Assessment:** xis.ai Full Stack Technical Assessment, Version 3.0  
**Branch:** `dev-test01`  
**Base CVAT commit:** `a81ed252dce15b805d5a544116cf98005e42f257`  
**Start:** 28 October 2026 (local date; record exact start time when work begins)

## Order and time budget

| Elapsed time | Work |
| --- | --- |
| 0:00-0:30 | Inspect CVAT API, data models, app registration, and permissions; record the plan before code. |
| 0:30-2:00 | Create the `cvat/apps/test` Django app and a task annotation-count endpoint using database aggregation. Commit the endpoint. |
| 2:00-3:00 | Verify counts against a known task and add focused endpoint coverage; commit. |
| 3:00-4:45 | Add the UI page and graph, including empty and request-failure states; commit. |
| 4:45-5:30 | Apply existing login and task authorization conventions; demonstrate authorized and refused requests; commit. |
| 5:30-6:15 | Choose one additional grouping/filter and document the reason; commit. |
| 6:15-7:00 | Set and measure an endpoint latency target over five runs; save raw output and environment details. |
| 7:00-7:30 | If items 1-7 are complete, implement live WebSocket updates and reconnect behavior; otherwise record the stopping point. |
| 7:30-8:00 | Update Objectives and Definition of Done with evidence, review commits and docs, record the short Loom, and prepare the fork PR. |

## Scope and decisions

The first milestone is a database-backed per-class annotation count for one task. Follow CVAT's existing app, routing, query, and permission patterns, and keep the implementation inside the required new `test` Django app where practical. Annotation counting must account for the annotation types supported by the chosen query; this will be confirmed from the models before implementation.

The assessment explicitly prioritizes requirements 1-4. Work on the UI only after the endpoint is working. WebSocket updates and reconnect handling are deferred until the earlier requirements are complete. COCO import and a Loom recording depend on the local Docker stack and sample data being available; if unavailable within the time box, record the limitation and evidence rather than claim completion. No PR will target the upstream CVAT repository.

The additional requirement-7 feature is a filter by annotation source (`manual`, `auto`, `semi-auto`, `file`, or `consensus`). Source was chosen because it is recorded on every saved shape and lets a reviewer distinguish human work from imported or automated annotations without changing the useful per-class grouping.

## Completion rule

Stop at the eight-hour limit. Commit in small steps with messages that state what changed and why. Report each unfinished requirement and the reason in the final checklist. Do not report performance numbers without five raw measurements, the median and spread, machine details, and the base CVAT SHA.
