from app.database.database import connection_scope
from datetime import datetime
import uuid
import json



def create_topic(
    content_id: str,
    name: str,
    description: str,
    importance: int,
    difficulty: int,
    learning_objectives,
    concepts,
    practical_applications
):

    topic_id = str(uuid.uuid4())

    with connection_scope() as connection:

        connection.execute(
            """
            INSERT INTO topics (
                id,
                content_id,
                name,
                description,
                importance,
                difficulty,
                learning_objectives,
                concepts,
                practical_applications
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                topic_id,
                content_id,
                name,
                description,
                importance,
                difficulty,
                json.dumps(learning_objectives, ensure_ascii=False),
                json.dumps(concepts, ensure_ascii=False),
                json.dumps(practical_applications, ensure_ascii=False)
            )
        )

    return topic_id




def get_topic(topic_id: str):

    with connection_scope() as connection:

        result = connection.execute(
            """
            SELECT *
            FROM topics
            WHERE id = ?
            """,
            (topic_id,)
        ).fetchone()


    if not result:
        return None


    topic = dict(result)

    topic["learning_objectives"] = json.loads(
        topic["learning_objectives"]
    )

    topic["concepts"] = json.loads(
        topic["concepts"]
    )

    topic["practical_applications"] = json.loads(
        topic["practical_applications"]
    )


    return topic


def get_content_topics(content_id):

    with connection_scope() as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM topics
            WHERE content_id = ?
            """,
            (content_id,)
        ).fetchall()

    topics = []
    for row in rows:
        topic = dict(row)
        topic["learning_objectives"] = json.loads(
            topic["learning_objectives"]
        )
        topic["concepts"] = json.loads(topic["concepts"])
        topic["practical_applications"] = json.loads(
            topic["practical_applications"]
        )
        topics.append(topic)

    return topics


def update_topic(
    topic_id: str,
    name: str,
    description: str,
    learning_objectives: list[str],
    concepts: list[str],
    practical_applications: list[str] | None = None,
):
    with connection_scope() as connection:
        connection.execute(
            """
            UPDATE topics
            SET name = ?, description = ?, learning_objectives = ?,
                concepts = ?, practical_applications = ?
            WHERE id = ?
            """,
            (
                name,
                description,
                json.dumps(learning_objectives, ensure_ascii=False),
                json.dumps(concepts, ensure_ascii=False),
                json.dumps(practical_applications or [], ensure_ascii=False),
                topic_id,
            ),
        )

    return get_topic(topic_id)