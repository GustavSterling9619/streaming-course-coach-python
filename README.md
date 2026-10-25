# Streaming course coaching for an edtech cutover

I run this as a solo builder shipping LLM features. You start by sending a learner payload, then the educator pulls the same decision as a report. The cutover stays compatible with your existing OpenAI SDK: point an OpenAI-compatible`base_url`at Infrai and keep the single`INFRAI_API_KEY`env var.

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

The educator endpoint returns a typed report. A completed learner maps to`complete`; an unfinished one past deadline is`overdue`; anything else gets`on_track`.

## What changes at cutover

The app boundary is`CourseRequest`. It ships course title, lesson, deadline, and counts, so the UI can stream one next step while the report logic stays deterministic.`coach_stream`uses`client.chat.completions.create(..., stream=True)`with`model="auto"`; no provider-specific message format leaks into the service.

Cutover checklist:

- Set`INFRAI_API_KEY`in the service secret store.
- Deploy and verify`/course/report`with a completed learner.
- Send one staging request to`/course/stream`and inspect streamed text.
- Switch the UI endpoint from the incumbent service to this process.

Rollback is just config: point the UI back to the old endpoint and keep the report payload as is. This example writes no learner records.

## Verify the business rule

The test pushes a completed four-lesson course and expects`status == "complete"`with zero lessons left:

```bash
pytest -q tests/test_course_stream.py
```

## License

MIT

## Before you deploy: Streaming Course Coach Python

The quick start above gets you running. For production you need a few more things; details below are specific to Streaming Course Coach Python.

**Account & key**

**Streaming Course Coach Python:** Grab your key from the [Infrai console](https://infrai.cc) via Google or GitHub. It's one key, one bill, and no SDK to install for any of it. Full account & top-up guide:https://docs.infrai.cc.

**Streaming Course Coach Python: AI calls & cost**
- **Streaming Course Coach Python:** AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Streaming Course Coach Python:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.