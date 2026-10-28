# Definition of Done

Mark each item only when complete and add a concrete result, command output, or file/line reference beside it.

- [x] API returns per-class counts for a task from the database. Evidence: `GET /api/tasks/14/annotation-counts` returned HTTP 200 with per-label totals ([API response screenshot](evidence/task-14-annotation-counts-api-response.png)); aggregation is implemented in `cvat/apps/test/views.py`.
- [x] Known-task counts are checked against their annotations. Evidence: task 8 contains the 5,000-image COCO validation set; direct database aggregation returned examples including `airplane: 161`, `apple: 243`, and `bench: 557`.
- [x] UI calls the endpoint and renders a graph. Evidence: `/tasks/14/annotation-counts` rendered the per-label horizontal bar chart ([chart screenshot](evidence/task-14-annotation-counts-chart.png)) implemented in `cvat-ui/src/components/task-annotation-counts-page/`.
- [x] UI handles no annotations and a failed request. Evidence: the page renders an explicit empty state for zero counts and a retryable error alert for failed requests.
- [ ] Unauthenticated and unauthorized task access are refused; authorized access works. Evidence: pending.
- [ ] MO-1 is measured five times with raw output, median, spread, machine details, and base commit. Evidence: pending.
- [ ] One additional filter or grouping is implemented and its rationale recorded. Evidence: pending.
- [ ] Live graph updates and reconnect behavior are implemented, if time permits after requirements 1-4. Evidence: pending.
- [ ] Loom recording is five minutes or less and answers K1-K4 against the submitted code. Evidence: pending.
- [ ] All unfinished requirements and reasons are listed. Evidence: pending.
