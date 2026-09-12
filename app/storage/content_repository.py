from datetime import datetime
import uuid

from app.database.database import connection_scope


def create_content(
    teacher_id: str,
    title: str,
    original_text: str
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
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                content_id,
                teacher_id,
                title,
                original_text,
                created_at
            )
        )

    return content_id



def get_content(content_id: str):

    with connection_scope() as connection:

        result = connection.execute(
            """
            SELECT *
            FROM contents
            WHERE id = ?
            """,
            (content_id,)
        ).fetchone()

    if not result:
        return None

    return dict(result)



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