import sqlite3
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
    "subject": "TEXT NOT NULL DEFAULT ''",
    "education_level": "TEXT NOT NULL DEFAULT ''",
    "grade_or_period": "TEXT NOT NULL DEFAULT ''",
    "target_audience": "TEXT NOT NULL DEFAULT ''",
    "learning_goal": "TEXT NOT NULL DEFAULT ''",
    "assessment_focus": "TEXT NOT NULL DEFAULT '[]'",
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

        connection.commit()


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
