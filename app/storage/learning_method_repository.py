from app.database.database import connection_scope



def get_learning_methods():

    with connection_scope() as connection:

        rows = connection.execute(
            """
            SELECT *

            FROM learning_methods

            WHERE active = 1

            """
        ).fetchall()


    return [
        dict(row)
        for row in rows
    ]