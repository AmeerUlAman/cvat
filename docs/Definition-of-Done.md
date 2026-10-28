# Definition of Done

Mark each item only when complete and add a concrete result, command output, or file/line reference beside it.

- [x] API returns per-class counts for a task from the database. Evidence: `GET /api/tasks/14/annotation-counts` returned HTTP 200 with per-label totals ([API response screenshot](evidence/task-14-annotation-counts-api-response.png)); aggregation is implemented in `cvat/apps/test/views.py`.
- [x] Known-task counts are checked against their annotations. Evidence: task 8 contains the 5,000-image COCO validation set; direct database aggregation returned examples including `airplane: 161`, `apple: 243`, and `bench: 557`.
- [x] UI calls the endpoint and renders a graph. Evidence: `/tasks/14/annotation-counts` rendered the per-label horizontal bar chart ([chart screenshot](evidence/task-14-annotation-counts-chart.png)) implemented in `cvat-ui/src/components/task-annotation-counts-page/`.
- [x] UI handles no annotations and a failed request. Evidence: the page renders an explicit empty state for zero counts and a retryable error alert for failed requests.
- [x] Unauthenticated and unauthorized task access are refused; authorized access works. Evidence: a focused API-client check returned HTTP 401 for an anonymous request, HTTP 403 for an unrelated authenticated user, and HTTP 200 with 80 label groups for task 14's owner. The endpoint delegates the decision to CVAT's existing `TaskPermission` view policy.
- [x] MO-1 is measured five times with raw output, median, spread, machine details, and base commit. Evidence: `Objectives.md` records all five runs (120.987-149.311 ms), a 131.887 ms median, a 28.324 ms spread, the excluded warm-up, machine details, task size, and base SHA; the median meets the 200 ms target.
- [x] One additional filter or grouping is implemented and its rationale recorded. Evidence: the API and UI filter counts by annotation source; focused checks returned 41,866 `file` shapes and 3 `manual` shapes for task 14, while an unsupported source returned HTTP 400. `Plan.md` records why source is useful beyond a plain total, and the production UI build completed successfully.
- [ ] Live graph updates and reconnect behavior are implemented, if time permits after requirements 1-4. Evidence: pending.
- [ ] Loom recording is five minutes or less and answers K1-K4 against the submitted code. Evidence: pending.
- [ ] All unfinished requirements and reasons are listed. Evidence: pending.
