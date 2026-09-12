import uuid
from datetime import datetime

from app.database.database import connection_scope


def save_preference(
    student_id,
    content_id,
    topic_id,
    preferred_method
):

    preference_id = str(uuid.uuid4())

    with connection_scope() as connection:

        connection.execute(
            """
            INSERT INTO student_learning_preferences
            (
                id,
                student_id,
                content_id,
                topic_id,
                preferred_method,
                created_at
            )

            VALUES (?, ?, ?, ?, ?, ?)
            """,

            (
                preference_id,
                student_id,
                content_id,
                topic_id,
                preferred_method,
                datetime.now().isoformat()
            )
        )

    return preference_id



def get_preference(
    student_id,
    content_id
):

    with connection_scope() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM student_learning_preferences

            WHERE student_id = ?
            AND content_id = ?

            ORDER BY created_at DESC

            LIMIT 1
            """,

            (
                student_id,
                content_id
            )

        ).fetchone()


    return dict(row) if row else None