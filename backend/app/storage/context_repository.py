from datetime import datetime
import uuid

from app.database.database import connection_scope


def create_context(teacher_id: str, name: str, description: str = ""):
    context_id = str(uuid.uuid4())

    with connection_scope() as connection:
        connection.execute(
            """
            INSERT INTO contexts (id, teacher_id, name, description, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (context_id, teacher_id, name, description, datetime.now().isoformat()),
        )

    return get_context(context_id)


def get_context(context_id: str):
    with connection_scope() as connection:
        row = connection.execute(
            "SELECT * FROM contexts WHERE id = ?",
            (context_id,),
        ).fetchone()

    return dict(row) if row else None


def get_teacher_contexts(teacher_id: str):
    with connection_scope() as connection:
        rows = connection.execute(
            "SELECT * FROM contexts WHERE teacher_id = ? ORDER BY created_at DESC",
            (teacher_id,),
        ).fetchall()

    contexts = []
    for row in rows:
        context = dict(row)
        context["classrooms"] = []
        context["subjects"] = []
        contexts.append(context)

    return contexts