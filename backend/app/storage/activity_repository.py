from app.database.database import connection_scope

from datetime import datetime
import uuid
import json



def create_activity(
    topic_id: str,
    topic: str,
    learning_objective: str,
    activity_type: str,
    difficulty: int,
    cognitive_skill: str,
    learning_dimension: str,
    question: str,
    options: list[str],
    correct_answer: str,
    explanation: str,
    hints: list[str],
    review_status: str = "pending",
    validation_score: int | None = None,
    validation_warnings: list[str] = None,
    teacher_modified: bool = False,
    regenerated_from: str | None = None
):

    activity_id = str(uuid.uuid4())


    if validation_warnings is None:
        validation_warnings = []


    with connection_scope() as connection:

        connection.execute(
            """
            INSERT INTO activities (
                id,
                topic_id,
                topic,
                learning_objective,
                type,
                difficulty,
                cognitive_skill,
                learning_dimension,
                question,
                options,
                correct_answer,
                explanation,
                hints,
                review_status,
                validation_score,
                validation_warnings,
                teacher_modified,
                regenerated_from
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
    activity_id,
    topic_id,
    topic,
    learning_objective,
    activity_type,
    difficulty,
    cognitive_skill,
    learning_dimension,
    question,
    json.dumps(options, ensure_ascii=False),
    correct_answer,
    explanation,
    json.dumps(hints, ensure_ascii=False),
    review_status,
    validation_score,
    json.dumps(validation_warnings, ensure_ascii=False),
    1 if teacher_modified else 0,
    regenerated_from
)
        )


    return activity_id





def get_activity(activity_id: str):

    with connection_scope() as connection:

        result = connection.execute(
            """
            SELECT *
            FROM activities
            WHERE id = ?
            """,
            (activity_id,)
        ).fetchone()


    if not result:
        return None


    return _convert_activity(result)





def get_topic_activities(topic_id: str):

    with connection_scope() as connection:

        results = connection.execute(
            """
            SELECT *
            FROM activities
            WHERE topic_id = ?
            """,
            (topic_id,)
        ).fetchall()


    return [
        _convert_activity(row)
        for row in results
    ]





def get_approved_activities(topic_id: str):

    with connection_scope() as connection:

        results = connection.execute(
            """
            SELECT *
            FROM activities
            WHERE topic_id = ?
            AND review_status = 'approved'
            """,
            (topic_id,)
        ).fetchall()


    return [
        _convert_activity(row)
        for row in results
    ]





def update_review_status(
    activity_id: str,
    review_status: str,
    teacher_modified: bool = False
):

    with connection_scope() as connection:

        connection.execute(
            """
            UPDATE activities
            SET
                review_status = ?,
                teacher_modified = ?
            WHERE id = ?
            """,
            (
                review_status,
                1 if teacher_modified else 0,
                activity_id
            )
        )


def _convert_activity(row):

    activity = dict(row)
    activity["activity_id"] = activity["id"]

    activity["options"] = json.loads(
        activity["options"]
    )

    activity["hints"] = json.loads(
        activity["hints"]
    )

    activity["validation_warnings"] = json.loads(
        activity["validation_warnings"]
    )

    activity["teacher_modified"] = bool(
        activity["teacher_modified"]
    )

    return activity

def get_content_activities(content_id):

    with connection_scope() as connection:

        rows = connection.execute(
            """
            SELECT a.*

            FROM activities a

            INNER JOIN topics t
                ON a.topic_id = t.id

            WHERE t.content_id = ?

            """,
            (content_id,)
        ).fetchall()


    return [
        _convert_activity(row)
        for row in rows
    ]
def update_activity_review(

    activity_id: str,

    review_status: str,

    teacher_modified: bool = False,

    question=None,

    options=None,

    correct_answer=None,

    explanation=None,

    hints=None

):

    with connection_scope() as connection:

        connection.execute(

            """
            UPDATE activities

            SET

                review_status = ?,

                teacher_modified = ?,

                question = COALESCE(?, question),

                options = COALESCE(?, options),

                correct_answer = COALESCE(?, correct_answer),

                explanation = COALESCE(?, explanation),

                hints = COALESCE(?, hints)

            WHERE id = ?

            """,

            (

                review_status,

                1 if teacher_modified else 0,

                question,

                json.dumps(options)
                if options else None,

                correct_answer,

                explanation,

                json.dumps(hints)
                if hints else None,

                activity_id

            )

        )

def get_approved_activities_by_content(
    content_id: str
):

    with connection_scope() as connection:

        rows = connection.execute(
            """
            SELECT a.*

            FROM activities a

            INNER JOIN topics t
                ON a.topic_id = t.id

            WHERE t.content_id = ?

            AND a.review_status = 'approved'

            """,
            (
                content_id,
            )

        ).fetchall()


    return [
        _convert_activity(row)
        for row in rows
    ]

def get_pending_activities_by_content(

    content_id: str

):

    with connection_scope() as connection:

        rows = connection.execute(

            """
            SELECT a.*

            FROM activities a

            INNER JOIN topics t

                ON a.topic_id = t.id

            WHERE t.content_id = ?

            AND a.review_status = 'pending'

            """,

            (
                content_id,
            )

        ).fetchall()


    return [

        _convert_activity(row)

        for row in rows

    ]

def mark_activity_regenerated(
    activity_id: str
):

    with connection_scope() as connection:

        connection.execute(
            """
            UPDATE activities

            SET review_status = 'regenerated'

            WHERE id = ?

            """,
            (
                activity_id,
            )
        )