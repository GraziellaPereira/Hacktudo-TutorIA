from datetime import datetime
import uuid
import json

from app.database.database import connection_scope
from app.model.context import LearningContext



def create_content(

    teacher_id,

    title,

    original_text,

    context

):

    content_id = str(uuid.uuid4())

    created_at = datetime.now().isoformat()


    with connection_scope() as connection:

        connection.execute(

            """
            INSERT INTO contents (

                id,

                teacher_id,

                title,

                original_text,

                subject,

                education_level,

                grade_or_period,

                target_audience,

                learning_goal,

                assessment_focus,

                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """,

            (

                content_id,

                teacher_id,

                title,

                original_text,

                context.subject,

                context.education_level,

                context.grade_or_period,

                context.target_audience,

                context.learning_goal,

                json.dumps(
                    context.assessment_focus,
                    ensure_ascii=False
                ),

                created_at

            )

        )


    return content_id


def get_teacher_contents(teacher_id: str):

    with connection_scope() as connection:

        results = connection.execute(
            """
            SELECT *
            FROM contents
            WHERE teacher_id = ?
            ORDER BY created_at DESC
            """,
            (teacher_id,)
        ).fetchall()

    return [
        dict(row)
        for row in results
    ]


def get_content(content_id):

    with connection_scope() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM contents
            WHERE id = ?
            """,
            (content_id,)
        ).fetchone()

    return dict(row) if row else None

def get_content_context(content_id):

    with connection_scope() as connection:

        row = connection.execute(

            """
            SELECT *
            FROM contents
            WHERE id = ?
            """,

            (content_id,)

        ).fetchone()


    if not row:

        return None


    return LearningContext(

        subject=row["subject"],

        education_level=row["education_level"],

        grade_or_period=row["grade_or_period"],

        target_audience=row["target_audience"],

        learning_goal=row["learning_goal"],

        assessment_focus=json.loads(row["assessment_focus"] or "[]")

    )

def get_student_contents():

    with connection_scope() as connection:

        rows = connection.execute(
            """
            SELECT DISTINCT

                c.id,
                c.title,
                c.subject,
                c.education_level,
                c.grade_or_period,
                c.target_audience,
                c.learning_goal,
                c.created_at

            FROM contents c

            INNER JOIN topics t
                ON t.content_id = c.id

            INNER JOIN activities a
                ON a.topic_id = t.id

            WHERE a.review_status = 'approved'

            ORDER BY c.created_at DESC

            """
        ).fetchall()


    return [
        dict(row)
        for row in rows
    ]

def update_content_summary(
    content_id: str,
    summary: str
):

    with connection_scope() as connection:

        connection.execute(
            """
            UPDATE contents

            SET summary = ?

            WHERE id = ?

            """,
            (
                summary,
                content_id
            )
        )

def update_content_summary(
    content_id,
    summary
):

    with connection_scope() as connection:

        connection.execute(
            """
            UPDATE contents

            SET summary = ?

            WHERE id = ?

            """,
            (
                json.dumps(
                    summary,
                    ensure_ascii=False
                ),
                content_id
            )
        )