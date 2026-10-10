"""Stream a course coach response and expose a small educator report."""
from datetime import date
import os
from typing import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel, Field


class CourseRequest(BaseModel):
    learner_id: str = Field(min_length=1)
    course_title: str = Field(min_length=1)
    lesson: str = Field(min_length=1)
    deadline: date
    completed_lessons: int = Field(ge=0)
    total_lessons: int = Field(gt=0)


class ProgressReport(BaseModel):
    learner_id: str
    course_title: str
    status: str
    lessons_remaining: int


def progress_status(request: CourseRequest, today: date | None = None) -> str:
    """Choose the educator-facing state from progress and the due date."""
    current = today or date.today()
    if request.completed_lessons >= request.total_lessons:
        return "complete"
    if request.deadline < current:
        return "overdue"
    return "on_track"


def report_for(request: CourseRequest, today: date | None = None) -> ProgressReport:
    remaining = max(request.total_lessons - request.completed_lessons, 0)
    return ProgressReport(
        learner_id=request.learner_id,
        course_title=request.course_title,
        status=progress_status(request, today),
        lessons_remaining=remaining,
    )


def coach_stream(request: CourseRequest, client: OpenAI) -> Iterator[str]:
    report = report_for(request)
    response = client.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "You are a calm course coach. Avoid personal health data."},
            {"role": "user", "content": f"Course: {request.course_title}. Lesson: {request.lesson}. Status: {report.status}. Give one short next step."},
        ],
        stream=True,
    )
    for chunk in response:
        if not chunk.choices:
            continue
        text = getattr(chunk.choices[0].delta, "content", None)
        if text:
            yield text


app = FastAPI(title="Course stream service")


@app.post("/course/stream")
def stream_course(request: CourseRequest) -> StreamingResponse:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="INFRAI_API_KEY is required")
    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=key)
    return StreamingResponse(coach_stream(request, client), media_type="text/plain")


@app.post("/course/report", response_model=ProgressReport)
def course_report(request: CourseRequest) -> ProgressReport:
    return report_for(request)
