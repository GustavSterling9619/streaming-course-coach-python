from datetime import date
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.course_stream import CourseRequest, coach_stream, report_for


def test_completed_learner_is_reported_complete():
    request = CourseRequest(
        learner_id="learner-7",
        course_title="Medication safety",
        lesson="Final review",
        deadline=date(2026, 9, 30),
        completed_lessons=4,
        total_lessons=4,
    )
    report = report_for(request, today=date(2026, 9, 7))
    assert report.status == "complete"
    assert report.lessons_remaining == 0


def test_coach_stream_skips_empty_choices():
    request = CourseRequest(
        learner_id="learner-7",
        course_title="Medication safety",
        lesson="Final review",
        deadline=date(2026, 9, 30),
        completed_lessons=3,
        total_lessons=4,
    )
    chunks = [
        SimpleNamespace(choices=[]),
        SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="Review the final lesson."))]),
        SimpleNamespace(choices=[]),
    ]
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: chunks)))

    assert list(coach_stream(request, client)) == ["Review the final lesson."]
