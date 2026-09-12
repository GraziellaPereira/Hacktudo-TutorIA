from app.database.database import connection_scope

from datetime import datetime
import uuid



def create_attempt(
    student_id: str,
    activity_id: str,
    topic: str,
    method: str,
    selected_answer: str,
    correct_answer: str,
    is_correct: bool,
    difficulty: int,
    learning_dimension: str,
    response_time_seconds: float | None = None
):

    attempt_id = str(uuid.uuid4())

    created_at = datetime.now().isoformat()


    with connection_scope() as connection:

        connection.execute(
            """
            INSERT INTO attempts (
                id,
                student_id,
                activity_id,
                topic,
                method,
                selected_answer,
                correct_answer,
                is_correct,
                difficulty,
                learning_dimension,
                response_time_seconds,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt_id,
                student_id,
                activity_id,
                topic,
                method,
                selected_answer,
                correct_answer,
                1 if is_correct else 0,
                difficulty,
                learning_dimension,
                response_time_seconds,
                created_at
            )
        )


    return attempt_id





def get_student_attempts(student_id: str):

    with connection_scope() as connection:

        results = connection.execute(
            """
            SELECT *
            FROM attempts
            WHERE student_id = ?
            ORDER BY created_at DESC
            """,
            (student_id,)
        ).fetchall()


    return [
        dict(row)
        for row in results
    ]





def get_topic_performance(
    student_id: str,
    topic: str
):

    with connection_scope() as connection:

        result = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(is_correct) AS correct
            FROM attempts
            WHERE student_id = ?
            AND topic = ?
            """,
            (
                student_id,
                topic
            )
        ).fetchone()


    if not result or result["total"] == 0:
        return {
            "total":0,
            "accuracy":0
        }


    return {
        "total": result["total"],
        "correct": result["correct"],
        "accuracy":
            (result["correct"] / result["total"]) * 100
    }