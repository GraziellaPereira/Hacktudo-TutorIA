from app.database.database import initialize_database, connection_scope

from app.storage.attempt_repository import (
    create_attempt,
    get_student_attempts,
    get_topic_performance
)

from app.storage.activity_repository import get_activity



# Inicializa banco
initialize_database()



# ===============================
# Criar aluno de teste
# ===============================

student_id = "student_1"


with connection_scope() as connection:

    exists = connection.execute(
        """
        SELECT id
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    ).fetchone()


    if not exists:

        connection.execute(
            """
            INSERT INTO students (
                id,
                name,
                education_level,
                grade_or_period,
                created_at
            )
            VALUES (?, ?, ?, ?, datetime('now'))
            """,
            (
                student_id,
                "Maria Silva",
                "Ensino Médio",
                "3º ano"
            )
        )


print("Aluno criado/verificado:")
print(student_id)




# ===============================
# Verificar atividade existente
# ===============================

activity_id = "05c0d3ce-5e6c-46fd-8794-92946a7e65db"


activity = get_activity(
    activity_id
)


if not activity:

    raise RuntimeError(
        "A atividade de teste não existe. "
        "Execute primeiro o teste de activity_repository."
    )


print("\nAtividade encontrada:")
print(activity["question"])




# ===============================
# Criar tentativa
# ===============================

attempt_id = create_attempt(

    student_id=student_id,

    activity_id=activity_id,

    topic=activity["topic"],

    method="mind_map",

    selected_answer="P(x)=4x+2",

    correct_answer=activity["correct_answer"],

    is_correct=False,

    difficulty=activity["difficulty"],

    learning_dimension=activity["learning_dimension"],

    response_time_seconds=35

)


print("\nID tentativa:")
print(attempt_id)




# ===============================
# Buscar tentativas do aluno
# ===============================

print("\n==============================")
print("TENTATIVAS DO ALUNO")
print("==============================")


attempts = get_student_attempts(
    student_id
)


for attempt in attempts:

    print(attempt)




# ===============================
# Desempenho por tópico
# ===============================

print("\n==============================")
print("DESEMPENHO")
print("==============================")


performance = get_topic_performance(

    student_id,

    activity["topic"]

)


print(performance)