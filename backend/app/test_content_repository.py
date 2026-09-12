from datetime import datetime

from app.database.database import connection_scope, initialize_database
from app.storage.content_repository import (
    create_content,
    get_content
)


initialize_database()

with connection_scope() as connection:
    connection.execute(
        """
        INSERT OR IGNORE INTO teachers (id, name, email, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            "prof_1",
            "Professor de teste",
            "prof_1@example.com",
            datetime.now().isoformat(),
        ),
    )


content_id = create_content(
    teacher_id="prof_1",
    title="Funções",
    original_text="Conteúdo de matemática sobre funções."
)


print("ID criado:")
print(content_id)


content = get_content(content_id)


print("\nConteúdo:")
print(content)