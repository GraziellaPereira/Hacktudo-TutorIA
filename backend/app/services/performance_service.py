import random
from datetime import datetime
from collections import defaultdict, Counter
from math import ceil

from app.model.activity import Activity
from app.model.attempt import StudentAttempt

def calculate_error_profile(attempts):
    errors = [
        attempt.learning_dimension
        for attempt in attempts
        if not attempt.is_correct
    ]

    return Counter(errors)


def has_improved(previous_attempts, current_attempts) -> bool:
    previous_accuracy = calculate_accuracy(previous_attempts)
    current_accuracy = calculate_accuracy(current_attempts)
    previous_errors = sum(not attempt.is_correct for attempt in previous_attempts)
    current_errors = sum(not attempt.is_correct for attempt in current_attempts)

    return (
        current_accuracy > previous_accuracy
        or current_errors < previous_errors
    )


def has_mastered(attempts, minimum_attempts: int = 10) -> bool:
    if len(attempts) < minimum_attempts:
        return False

    error_profile = calculate_error_profile(attempts)
    return calculate_accuracy(attempts) >= 0.8 and not any(
        count >= 2 for count in error_profile.values()
    )

def calculate_accuracy(
    attempts: list[StudentAttempt],
) -> float:
    if not attempts:
        return 0.0

    correct_answers = sum(
        attempt.is_correct
        for attempt in attempts
    )

    return correct_answers / len(attempts)


def recommend_method(error_profile, used_methods=None):
    used_methods = used_methods or set()

    mapping = {
        "concept": "flashcards",
        "relationship": "mind_map",
        "specific_information": "infographic",
        "application": "flashcards",
        "interpretation": "mind_map",
    }

    if not error_profile:
        return "flashcards"

    ordered_errors = sorted(
        error_profile.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    for error_type, _ in ordered_errors:
        method = mapping[error_type]

        if method not in used_methods:
            return method

    for method in ("flashcards", "mind_map", "infographic"):
        if method not in used_methods:
            return method

    return None

def register_attempt(
    student_id: str,
    activity: Activity,
    method: str | None,
    selected_answer: str,
    response_time_seconds: float | None = None,
) -> StudentAttempt:
    normalized_selected = selected_answer.strip()
    normalized_correct = activity.correct_answer.strip()

    return StudentAttempt(
        student_id=student_id,
        activity_id=activity.activity_id,
        topic=activity.topic,
        method=method,
        selected_answer=normalized_selected,
        correct_answer=normalized_correct,
        is_correct=normalized_selected == normalized_correct,
        difficulty=activity.difficulty,
        learning_dimension=activity.learning_dimension,
        response_time_seconds=response_time_seconds,
        created_at=datetime.now(),
    )


def select_activity_batch(
    activities: list[Activity],
    answered_ids: set[str],
    batch_size: int | None = None,
) -> list[Activity]:
    grouped = defaultdict(list)
    totals_by_topic = defaultdict(int)

    for activity in activities:
        totals_by_topic[activity.topic] += 1
        if activity.activity_id not in answered_ids:
            grouped[activity.topic].append(activity)

    selected = []
    for topic, available in grouped.items():
        random.shuffle(available)
        required = max(1, ceil(totals_by_topic[topic] / 3))
        selected.extend(available[:required])

    if batch_size is not None and len(selected) < batch_size:
        selected_ids = {activity.activity_id for activity in selected}
        remaining = [
            activity
            for activity in activities
            if activity.activity_id not in answered_ids
            and activity.activity_id not in selected_ids
        ]
        random.shuffle(remaining)
        selected.extend(remaining[: batch_size - len(selected)])

    random.shuffle(selected)

    return selected