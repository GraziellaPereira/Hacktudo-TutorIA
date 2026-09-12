from app.database.database import connection_scope


with connection_scope() as connection:

    rows = connection.execute(
        """
        SELECT
            id,
            teacher_id,
            title,
            created_at
        FROM contents
        ORDER BY created_at DESC
        """
    ).fetchall()


print("==============================")
print("CONTEÚDOS")
print("==============================")


for row in rows:
    print(dict(row))