from app.database.database import initialize_database, connection_scope


initialize_database()


with connection_scope() as connection:

    connection.execute(
        """
        INSERT INTO teachers (
            id,
            name,
            email,
            created_at
        )
        VALUES (?, ?, ?, datetime('now'))
        """,
        (
            "1",
            "Professor Teste",
            "professor@email.com"
        )
    )


print("Professor criado")