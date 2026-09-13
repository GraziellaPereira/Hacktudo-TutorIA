import sqlite3
import json
import uuid
from pathlib import Path
from typing import Iterator
from contextlib import contextmanager


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "tutoria.db"


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teachers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    email TEXT UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contexts (
    id TEXT PRIMARY KEY,
    teacher_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    classrooms TEXT NOT NULL DEFAULT '[]',
    subjects TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
);

CREATE TABLE IF NOT EXISTS classrooms (
    id TEXT PRIMARY KEY,
    context_id TEXT NOT NULL,
    name TEXT NOT NULL,
    year TEXT NOT NULL DEFAULT '',
    education_levels TEXT NOT NULL DEFAULT '[]',
    learning_objective TEXT NOT NULL DEFAULT '',
    question_focus TEXT NOT NULL DEFAULT '',
    students_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (context_id) REFERENCES contexts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subjects (
    id TEXT PRIMARY KEY,
    context_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    importance_level TEXT NOT NULL DEFAULT 'Medium',
    files TEXT NOT NULL DEFAULT '{}',
    activities TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    FOREIGN KEY (context_id) REFERENCES contexts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS classroom_subjects (
    classroom_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    PRIMARY KEY (classroom_id, subject_id),
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    education_level TEXT NOT NULL,
    grade_or_period TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contents (

    id TEXT PRIMARY KEY,

    teacher_id TEXT NOT NULL,

    title TEXT NOT NULL,

    original_text TEXT NOT NULL,

    summary TEXT,

    review_status TEXT NOT NULL DEFAULT 'pending',

    subject TEXT NOT NULL,

    education_level TEXT NOT NULL,

    grade_or_period TEXT NOT NULL,

    target_audience TEXT NOT NULL,

    learning_goal TEXT NOT NULL,

    assessment_focus TEXT NOT NULL,

    created_at TEXT NOT NULL,

    FOREIGN KEY (teacher_id) REFERENCES teachers(id)

);

CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    content_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    importance INTEGER NOT NULL,
    difficulty INTEGER NOT NULL,
    learning_objectives TEXT NOT NULL,
    concepts TEXT NOT NULL,
    practical_applications TEXT NOT NULL,
    FOREIGN KEY (content_id) REFERENCES contents(id)
);

CREATE TABLE IF NOT EXISTS activities (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    learning_objective TEXT NOT NULL,
    type TEXT NOT NULL,
    difficulty INTEGER NOT NULL,
    cognitive_skill TEXT NOT NULL,
    learning_dimension TEXT NOT NULL,
    question TEXT NOT NULL,
    options TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    explanation TEXT NOT NULL,
    hints TEXT NOT NULL,
    review_status TEXT NOT NULL,
    validation_score INTEGER,
    validation_warnings TEXT NOT NULL,
    teacher_modified INTEGER NOT NULL DEFAULT 0,
    regenerated_from TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

CREATE TABLE IF NOT EXISTS attempts (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    activity_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    method TEXT,
    selected_answer TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    difficulty INTEGER NOT NULL,
    learning_dimension TEXT NOT NULL,
    response_time_seconds REAL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (activity_id) REFERENCES activities(id)
);

CREATE TABLE IF NOT EXISTS learning_materials (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    content_id TEXT NOT NULL,
    topic_id TEXT,
    method TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    payload TEXT NOT NULL,
    material TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (content_id) REFERENCES contents(id)
);

CREATE TABLE IF NOT EXISTS student_contents (

    id TEXT PRIMARY KEY,

    student_id TEXT NOT NULL,

    content_id TEXT NOT NULL,

    created_at TEXT NOT NULL,

    FOREIGN KEY(student_id)
        REFERENCES students(id),

    FOREIGN KEY(content_id)
        REFERENCES contents(id),

    UNIQUE(student_id, content_id)

);

CREATE TABLE IF NOT EXISTS learning_methods (

    id TEXT PRIMARY KEY,

    name TEXT NOT NULL,

    description TEXT NOT NULL,

    active INTEGER DEFAULT 1

);

CREATE TABLE IF NOT EXISTS student_learning_preferences (

    id TEXT PRIMARY KEY,

    student_id TEXT NOT NULL,

    content_id TEXT NOT NULL,

    topic_id TEXT,

    preferred_method TEXT NOT NULL,

    created_at TEXT NOT NULL

);

CREATE TABLE IF NOT EXISTS student_activity_attempts (

    id TEXT PRIMARY KEY,

    student_id TEXT NOT NULL,

    material_id TEXT NOT NULL,

    item_id TEXT NOT NULL,

    item_type TEXT NOT NULL,

    concept TEXT,

    correct INTEGER NOT NULL,

    response_time_seconds INTEGER DEFAULT 0,

    created_at TEXT NOT NULL

);

CREATE TABLE IF NOT EXISTS student_recommendations (

    id TEXT PRIMARY KEY,

    student_id TEXT NOT NULL,

    content_id TEXT NOT NULL,

    status TEXT NOT NULL,

    action TEXT NOT NULL,

    method TEXT,

    reason TEXT,

    created_at TEXT NOT NULL

);

"""


CONTENT_CONTEXT_COLUMNS = {
    "summary": "TEXT",
    "attachment_path": "TEXT",
    "attachment_name": "TEXT",
    "review_status": "TEXT NOT NULL DEFAULT 'pending'",
    "subject": "TEXT NOT NULL DEFAULT ''",
    "education_level": "TEXT NOT NULL DEFAULT ''",
    "grade_or_period": "TEXT NOT NULL DEFAULT ''",
    "target_audience": "TEXT NOT NULL DEFAULT ''",
    "learning_goal": "TEXT NOT NULL DEFAULT ''",
    "assessment_focus": "TEXT NOT NULL DEFAULT '[]'",
        "context_id": "TEXT",
        "classroom_id": "TEXT",
        "subject_id": "TEXT",
}

CONTEXT_COLUMNS = {
    "classrooms": "TEXT NOT NULL DEFAULT '[]'",
    "subjects": "TEXT NOT NULL DEFAULT '[]'",
}

TEACHER_COLUMNS = {
    "description": "TEXT NOT NULL DEFAULT ''",
}

ACTIVITY_COLUMNS = {
    "regenerated_from": "TEXT",
}

LEARNING_MATERIAL_COLUMNS = {
    "content_id": "TEXT",
    "topic_id": "TEXT",
    "title": "TEXT NOT NULL DEFAULT ''",
    "summary": "TEXT NOT NULL DEFAULT ''",
    "payload": "TEXT NOT NULL DEFAULT '{}'",
    "material": "TEXT",
}


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(SCHEMA)
        existing_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(contents)")
        }

        for column, definition in CONTENT_CONTEXT_COLUMNS.items():
            if column not in existing_columns:
                connection.execute(
                    f"ALTER TABLE contents ADD COLUMN {column} {definition}"
                )

        teacher_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(teachers)")
        }
        for column, definition in TEACHER_COLUMNS.items():
            if column not in teacher_columns:
                connection.execute(
                    f"ALTER TABLE teachers ADD COLUMN {column} {definition}"
                )

        context_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(contexts)")
        }
        for column, definition in CONTEXT_COLUMNS.items():
            if column not in context_columns:
                connection.execute(
                    f"ALTER TABLE contexts ADD COLUMN {column} {definition}"
                )

        activity_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(activities)")
        }
        for column, definition in ACTIVITY_COLUMNS.items():
            if column not in activity_columns:
                connection.execute(
                    f"ALTER TABLE activities ADD COLUMN {column} {definition}"
                )

        material_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(learning_materials)"
            )
        }
        for column, definition in LEARNING_MATERIAL_COLUMNS.items():
            if column not in material_columns:
                connection.execute(
                    f"ALTER TABLE learning_materials ADD COLUMN {column} {definition}"
                )

        material_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(learning_materials)"
            )
        }
        if "material" in material_columns and "payload" in material_columns:
            connection.execute(
                "UPDATE learning_materials SET material = payload "
                "WHERE material IS NULL"
            )

        connection.executemany(
            """
            INSERT OR IGNORE INTO learning_methods (
                id,
                name,
                description
            )
            VALUES (?, ?, ?)
            """,
            [
                (
                    "flashcards",
                    "Flashcards",
                    "Cartões de pergunta e resposta para revisão",
                ),
                (
                    "mind_map",
                    "Mapa mental",
                    "Organização visual dos conceitos principais",
                ),
                (
                    "infographic",
                    "Infográfico",
                    "Resumo visual dos conceitos principais",
                ),
                (
                    "quiz",
                    "Quiz",
                    "Teste de conhecimento com questões",
                ),
                (
                    "explanation",
                    "Explicação guiada",
                    "Explicação passo a passo adaptada ao aluno",
                ),
            ],
        )

        connection.execute(
            """
            UPDATE learning_methods
            SET active = 0
            WHERE id IN ('quiz', 'explanation')
            """
        )

        _migrate_legacy_contexts(connection)

        connection.commit()


def _migrate_legacy_contexts(connection: sqlite3.Connection) -> None:
    contexts = connection.execute(
        "SELECT id, classrooms, subjects FROM contexts"
    ).fetchall()

    for context in contexts:
        existing = connection.execute(
            "SELECT 1 FROM classrooms WHERE context_id = ? LIMIT 1",
            (context[0],),
        ).fetchone()
        if existing:
            continue

        classrooms = json.loads(context[1] or "[]")
        subjects = json.loads(context[2] or "[]")
        subject_ids = {}

        for raw_subject in subjects:
            subject = _normalize_legacy_subject(raw_subject)
            subject_id = str(subject.get("id") or uuid.uuid4())
            subject_ids[subject_id] = subject
            connection.execute(
                """
                INSERT OR IGNORE INTO subjects
                (id, context_id, name, description, importance_level, files, activities, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    subject_id,
                    context[0],
                    subject.get("name", ""),
                    subject.get("description", ""),
                    subject.get("importanceLevel", "Medium"),
                    json.dumps(subject.get("files", {}), ensure_ascii=False),
                    json.dumps(subject.get("activities", []), ensure_ascii=False),
                ),
            )

        for classroom in classrooms:
            classroom_id = str(classroom.get("id") or uuid.uuid4())
            connection.execute(
                """
                INSERT OR IGNORE INTO classrooms
                (id, context_id, name, year, education_levels, learning_objective, question_focus, students_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    classroom_id,
                    context[0],
                    classroom.get("name", ""),
                    str(classroom.get("year", "")),
                    json.dumps(classroom.get("educationLevels", []), ensure_ascii=False),
                    classroom.get("learningObjective", ""),
                    classroom.get("questionFocus", ""),
                    int(classroom.get("studentsCount", 0) or 0),
                ),
            )
            for raw_subject in classroom.get("subjects", []):
                subject = _normalize_legacy_subject(raw_subject)
                subject_id = str(subject.get("id") or uuid.uuid4())
                if subject_id not in subject_ids:
                    subject_ids[subject_id] = subject
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO subjects
                        (id, context_id, name, description, importance_level, files, activities, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                        """,
                        (
                            subject_id,
                            context[0],
                            subject.get("name", ""),
                            subject.get("description", ""),
                            subject.get("importanceLevel", "Medium"),
                            json.dumps(subject.get("files", {}), ensure_ascii=False),
                            json.dumps(subject.get("activities", []), ensure_ascii=False),
                        ),
                    )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO classroom_subjects (classroom_id, subject_id)
                    VALUES (?, ?)
                    """,
                    (classroom_id, subject_id),
                )


def _normalize_legacy_subject(subject) -> dict:
    if isinstance(subject, dict):
        return subject
    if isinstance(subject, str):
        return {
            "name": subject,
            "description": "",
            "importanceLevel": "Medium",
            "files": {},
            "activities": [],
        }
    return {
        "name": "",
        "description": "",
        "importanceLevel": "Medium",
        "files": {},
        "activities": [],
    }


@contextmanager
def connection_scope() -> Iterator[sqlite3.Connection]:
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
