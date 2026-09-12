import uuid
import json
from datetime import datetime

from app.database.database import connection_scope



def create_learning_material(
    student_id,
    content_id,
    topic_id,
    method,
    material
):

    material_id = str(uuid.uuid4())
    serialized_material = json.dumps(
        material,
        ensure_ascii=False
    )

    with connection_scope() as connection:

        connection.execute(
            """
            INSERT INTO learning_materials
            (
                id,
                student_id,
                content_id,
                topic_id,
                method,
                title,
                summary,
                payload,
                material,
                created_at
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """,
            (
                material_id,
                student_id,
                content_id,
                topic_id,
                method,
                material.get("title", ""),
                material.get("summary", ""),
                serialized_material,
                serialized_material,
                datetime.now().isoformat()
            )
        )

    return material_id




def get_learning_materials(
    student_id,
    content_id
):

    with connection_scope() as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM learning_materials

            WHERE student_id = ?
            AND content_id = ?

            ORDER BY created_at DESC

            """,
            (
                student_id,
                content_id
            )

        ).fetchall()


    result = []

    for row in rows:

        item = dict(row)

        item["material"] = json.loads(
            item["material"]
        )

        result.append(item)


    return result