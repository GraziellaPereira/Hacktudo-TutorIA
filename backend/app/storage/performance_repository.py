from app.database.database import connection_scope



def get_student_performance_by_concept(
    student_id: str
):

    with connection_scope() as connection:

        rows = connection.execute(
            """
            SELECT
                concept,
                COUNT(*) AS attempts,
                COALESCE(a.learning_dimension, 'concept') AS learning_dimension,
                SUM(
                    CASE 
                        WHEN correct = 0 
                        THEN 1 
                        ELSE 0 
                    END
                ) AS errors,
                SUM(
                    CASE 
                        WHEN correct = 1 
                        THEN 1 
                        ELSE 0 
                    END
                ) AS correct_answers

            FROM student_activity_attempts

            LEFT JOIN activities a
                ON a.id = student_activity_attempts.item_id

            WHERE student_id = ?

            GROUP BY concept, learning_dimension

            ORDER BY errors DESC

            """,
            (
                student_id,
            )

        ).fetchall()


    performance = []

    for row in rows:

        item = dict(row)

        attempts = item["attempts"]

        item["error_rate"] = round(
            item["errors"] / attempts,
            2
        )

        performance.append(item)


    return performance