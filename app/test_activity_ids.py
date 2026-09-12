from app.database.database import connection_scope


with connection_scope() as connection:

    rows = connection.execute(
        """
        SELECT 
            id,
            question,
            review_status
        FROM activities
        """
    ).fetchall()


for row in rows:
    print(dict(row))