from datetime import datetime
import uuid

from app.database.database import connection_scope


def create_student(
    name: str,
    education_level: str,
    grade_or_period: str
):

    student_id = str(uuid.uuid4())

    with connection_scope() as connection:

        connection.execute(
            """
            INSERT INTO students (
                id,
                name,
                education_level,
                grade_or_period,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                student_id,
                name,
                education_level,
                grade_or_period,
                datetime.now().isoformat()
            )
        )

    return student_id



def get_student(student_id: str):

    with connection_scope() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM students
            WHERE id = ?
            """,
            (student_id,)
        ).fetchone()


    return dict(row) if row else None



def get_students():

    with connection_scope() as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM students
            ORDER BY created_at DESC
            """
        ).fetchall()


    return [
        dict(row)
        for row in rows
    ]