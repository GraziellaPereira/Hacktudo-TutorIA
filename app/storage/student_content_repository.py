from datetime import datetime
import uuid

from app.database.database import connection_scope



def create_student_content(
    student_id: str,
    content_id: str
):

    relation_id = str(uuid.uuid4())


    with connection_scope() as connection:

        connection.execute(
            """
            INSERT INTO student_contents (

                id,
                student_id,
                content_id,
                created_at

            )

            VALUES (?, ?, ?, ?)

            """,
            (
                relation_id,
                student_id,
                content_id,
                datetime.now().isoformat()
            )
        )


    return relation_id



def get_student_contents(
    student_id: str
):

    with connection_scope() as connection:

        rows = connection.execute(
            """
            SELECT

                c.id,
                c.title,
                c.subject,
                c.education_level,
                c.grade_or_period,
                c.target_audience,
                c.learning_goal,
                c.created_at

            FROM contents c

            INNER JOIN student_contents sc

                ON sc.content_id = c.id

            WHERE sc.student_id = ?

            ORDER BY c.created_at DESC

            """,
            (
                student_id,
            )

        ).fetchall()


    return [
        dict(row)
        for row in rows
    ]



def remove_student_content(
    student_id: str,
    content_id: str
):

    with connection_scope() as connection:

        connection.execute(
            """
            DELETE FROM student_contents

            WHERE student_id = ?

            AND content_id = ?

            """,
            (
                student_id,
                content_id
            )
        )