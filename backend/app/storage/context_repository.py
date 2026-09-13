from datetime import datetime
import json
import uuid

from app.database.database import connection_scope


def create_context(teacher_id: str, name: str, description: str = ""):
    context_id = str(uuid.uuid4())

    with connection_scope() as connection:
        connection.execute(
            """
            INSERT INTO contexts (id, teacher_id, name, description, classrooms, subjects, created_at)
            VALUES (?, ?, ?, ?, '[]', '[]', ?)
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

    if not row:
        return None

    return _context_with_structure(dict(row))


def get_teacher_contexts(teacher_id: str):
    with connection_scope() as connection:
        rows = connection.execute(
            "SELECT * FROM contexts WHERE teacher_id = ? ORDER BY created_at DESC",
            (teacher_id,),
        ).fetchall()

    contexts = []
    for row in rows:
        contexts.append(_context_with_structure(dict(row)))

    return contexts


def update_context_structure(context_id: str, classrooms: list, subjects: list | None = None):
    subjects = [_normalize_subject(subject) for subject in (subjects or [])]
    classrooms = [
        {
            **classroom,
            "subjects": [
                _normalize_subject(subject)
                for subject in classroom.get("subjects", [])
            ],
        }
        for classroom in classrooms
    ]

    with connection_scope() as connection:
        connection.execute(
            """
            UPDATE contexts
            SET classrooms = ?, subjects = ?
            WHERE id = ?
            """,
            (
                json.dumps(classrooms, ensure_ascii=False),
                json.dumps(subjects, ensure_ascii=False),
                context_id,
            ),
        )

        connection.execute("DELETE FROM classroom_subjects WHERE classroom_id IN (SELECT id FROM classrooms WHERE context_id = ?)", (context_id,))
        connection.execute("DELETE FROM classrooms WHERE context_id = ?", (context_id,))
        connection.execute("DELETE FROM subjects WHERE context_id = ?", (context_id,))

        subject_ids = {}
        for subject in subjects:
            subject_id = str(subject.get("id") or uuid.uuid4())
            subject_ids[subject_id] = subject
            connection.execute(
                """
                INSERT INTO subjects (id, context_id, name, description, importance_level, files, activities, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    subject_id,
                    context_id,
                    subject.get("name", ""),
                    subject.get("description", ""),
                    subject.get("importanceLevel", "Medium"),
                    json.dumps(subject.get("files", {}), ensure_ascii=False),
                    json.dumps(subject.get("activities", []), ensure_ascii=False),
                    datetime.now().isoformat(),
                ),
            )

        for classroom in classrooms:
            classroom_id = str(classroom.get("id") or uuid.uuid4())
            connection.execute(
                """
                INSERT INTO classrooms (id, context_id, name, year, education_levels, learning_objective, question_focus, students_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    classroom_id,
                    context_id,
                    classroom.get("name", ""),
                    str(classroom.get("year", "")),
                    json.dumps(classroom.get("educationLevels", []), ensure_ascii=False),
                    classroom.get("learningObjective", ""),
                    classroom.get("questionFocus", ""),
                    int(classroom.get("studentsCount", 0) or 0),
                    datetime.now().isoformat(),
                ),
            )
            for subject in classroom.get("subjects", []):
                subject_id = str(subject.get("id"))
                if subject_id not in subject_ids:
                    subject_ids[subject_id] = subject
                    connection.execute(
                        """
                        INSERT INTO subjects (id, context_id, name, description, importance_level, files, activities, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            subject_id,
                            context_id,
                            subject.get("name", ""),
                            subject.get("description", ""),
                            subject.get("importanceLevel", "Medium"),
                            json.dumps(subject.get("files", {}), ensure_ascii=False),
                            json.dumps(subject.get("activities", []), ensure_ascii=False),
                            datetime.now().isoformat(),
                        ),
                    )
                connection.execute(
                    "INSERT OR IGNORE INTO classroom_subjects (classroom_id, subject_id) VALUES (?, ?)",
                    (classroom_id, subject_id),
                )

    return get_context(context_id)


def _normalize_subject(subject):
    if isinstance(subject, str):
        return {
            "id": str(uuid.uuid4()),
            "name": subject.strip(),
            "description": "",
            "importanceLevel": "Medium",
            "files": {},
            "activities": [],
        }

    return dict(subject)


def _context_with_structure(context: dict):
    with connection_scope() as connection:
        classrooms_rows = connection.execute(
            "SELECT * FROM classrooms WHERE context_id = ? ORDER BY created_at",
            (context["id"],),
        ).fetchall()
        subjects_rows = connection.execute(
            "SELECT * FROM subjects WHERE context_id = ? ORDER BY created_at",
            (context["id"],),
        ).fetchall()
        links = connection.execute(
            "SELECT classroom_id, subject_id FROM classroom_subjects"
        ).fetchall()

    if not classrooms_rows and not subjects_rows:
        context["classrooms"] = json.loads(context.get("classrooms") or "[]")
        context["subjects"] = json.loads(context.get("subjects") or "[]")
        return context

    subjects = {}
    for row in subjects_rows:
        subject = dict(row)
        subject["contextId"] = subject.pop("context_id")
        subject["importanceLevel"] = subject.pop("importance_level")
        subject["files"] = json.loads(subject["files"] or "{}")
        subject["activities"] = json.loads(subject["activities"] or "[]")
        subject.pop("created_at", None)
        subjects[subject["id"]] = subject

    classroom_subject_ids = {}
    for link in links:
        classroom_subject_ids.setdefault(link["classroom_id"], []).append(link["subject_id"])

    classrooms = []
    for row in classrooms_rows:
        classroom = dict(row)
        classroom["educationLevels"] = json.loads(classroom.pop("education_levels") or "[]")
        classroom["learningObjective"] = classroom.pop("learning_objective")
        classroom["questionFocus"] = classroom.pop("question_focus")
        classroom["studentsCount"] = classroom.pop("students_count")
        classroom.pop("context_id", None)
        classroom.pop("created_at", None)
        classroom["subjects"] = [
            subjects[subject_id]
            for subject_id in classroom_subject_ids.get(classroom["id"], [])
            if subject_id in subjects
        ]
        classrooms.append(classroom)

    context["classrooms"] = classrooms
    context["subjects"] = list(subjects.values())
    return context


def add_context_subject(context_id: str, subject: dict):
    context = get_context(context_id)
    if not context:
        return None

    subjects = context.get("subjects", [])
    subjects.append(subject)
    return update_context_structure(context_id, context.get("classrooms", []), subjects)


def update_context_subject(context_id: str, subject_id: str, classrooms: list):
    context = get_context(context_id)
    if not context:
        return None

    updated = False
    subjects = context.get("subjects", [])
    for subject in subjects:
        if str(subject.get("id")) == subject_id:
            subject["classrooms"] = classrooms
            updated = True

    for classroom in context.get("classrooms", []):
        for subject in classroom.get("subjects", []):
            if str(subject.get("id")) == subject_id:
                subject["classrooms"] = classrooms
                updated = True

    if not updated:
        return None

    return update_context_structure(
        context_id,
        context.get("classrooms", []),
        subjects,
    )