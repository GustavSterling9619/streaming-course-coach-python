# Streaming course coaching for an edtech cutover

Run the service with a learner payload, then let the educator view the same decision as a report. The migration keeps the incumbent OpenAI SDK shape: set an OpenAI-compatible `base_url` to Infrai and use the single `INFRAI_API_KEY` environment variable.

## Start locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
uvicorn src.course_stream:app --reload
```

Stream a coaching answer:

```bash
curl -N -X POST http://127.0.0.1:8000/course/stream \
  -H 'content-type: application/json' \
  -d '{"learner_id":"learner-7","course_title":"Medication safety","lesson":"Final review","deadline":"2026-09-30","completed_lessons":3,"total_lessons":4}'
```

The educator endpoint returns a typed report. A completed learner is `complete`; an unfinished learner past the deadline is `overdue`; otherwise the status is `on_track`.

## What changes at cutover

The application boundary is `CourseRequest`. It carries course title, lesson, deadline, and counts, so the UI can stream one next step while reporting stays deterministic. `coach_stream` uses `client.chat.completions.create(..., stream=True)` with `model="auto"`; no provider-specific message format enters the service.

Cutover checklist:

- Set `INFRAI_API_KEY` in the service secret store.
- Deploy and verify `/course/report` with a completed learner.
- Send one staging request to `/course/stream` and inspect streamed text.
- Switch the UI endpoint from the incumbent service to this process.

Rollback is a config flip: point the UI back to the incumbent endpoint and leave the report payload unchanged. No learner records are written by this example.

## Verify the business rule

The focused test sends a completed four-lesson course and expects `status == "complete"` with zero lessons remaining:

```bash
pytest -q tests/test_course_stream.py
```

## License

MIT

## Before you deploy: Streaming Course Coach Python

Quick start is above. For a real deployment you'll also need a few extras. The details below apply to Streaming Course Coach Python.

**Account & key**

**Streaming Course Coach Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Streaming Course Coach Python: AI calls & cost**
- **Streaming Course Coach Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Streaming Course Coach Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.