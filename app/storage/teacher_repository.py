from datetime import datetime
import uuid

from app.database.database import connection_scope


def create_teacher(
    name: str,
    description: str,
    email: str | None = None,
) -> str:
    teacher_id = str(uuid.uuid4())

    with connection_scope() as connection:
        connection.execute(
            """
            INSERT INTO teachers (id, name, description, email, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                teacher_id,
                name,
                description,
                email,
                datetime.now().isoformat(),
            ),
        )

    return teacher_id


def get_teacher(teacher_id: str):
    with connection_scope() as connection:
        row = connection.execute(
            "SELECT * FROM teachers WHERE id = ?",
            (teacher_id,),
        ).fetchone()

    return dict(row) if row else None


def get_teachers():
    with connection_scope() as connection:
        rows = connection.execute(
            "SELECT * FROM teachers ORDER BY created_at DESC"
        ).fetchall()

    return [dict(row) for row in rows]
