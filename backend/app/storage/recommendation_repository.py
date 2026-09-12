import uuid

from datetime import datetime

from app.database.database import connection_scope



def create_recommendation(

    student_id,

    content_id,

    status,

    action,

    method,

    reason

):

    recommendation_id = str(uuid.uuid4())

    created_at = datetime.now().isoformat()


    with connection_scope() as connection:

        connection.execute(

            """

            INSERT INTO student_recommendations (

                id,

                student_id,

                content_id,

                status,

                action,

                method,

                reason,

                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            """,

            (

                recommendation_id,

                student_id,

                content_id,

                status,

                action,

                method,

                reason,

                created_at

            )

        )


    return recommendation_id




def get_student_recommendations(

    student_id,

    content_id

):

    with connection_scope() as connection:

        rows = connection.execute(

            """

            SELECT *

            FROM student_recommendations

            WHERE student_id = ?

            AND content_id = ?

            ORDER BY created_at DESC

            """,

            (

                student_id,

                content_id

            )

        ).fetchall()


    return [

        dict(row)

        for row in rows

    ]