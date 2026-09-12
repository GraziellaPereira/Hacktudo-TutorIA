import uuid

from datetime import datetime

from app.database.database import connection_scope



def create_attempt(

    student_id,

    material_id,

    item_id,

    item_type,

    concept,

    correct,

    response_time_seconds=0

):

    attempt_id = str(
        uuid.uuid4()
    )


    with connection_scope() as connection:

        connection.execute(

            """
            INSERT INTO student_activity_attempts

            (
                id,
                student_id,
                material_id,
                item_id,
                item_type,
                concept,
                correct,
                response_time_seconds,
                created_at
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            """,

            (

                attempt_id,

                student_id,

                material_id,

                item_id,

                item_type,

                concept,

                1 if correct else 0,

                response_time_seconds,

                datetime.now().isoformat()

            )

        )


    return attempt_id



def get_student_attempts(

    student_id

):

    with connection_scope() as connection:

        rows = connection.execute(

            """

            SELECT *

            FROM student_activity_attempts

            WHERE student_id = ?

            ORDER BY created_at DESC

            """,

            (

                student_id,

            )

        ).fetchall()


    return [

        dict(row)

        for row in rows

    ]