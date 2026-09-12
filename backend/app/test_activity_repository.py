from app.database.database import initialize_database
from app.storage.activity_repository import (
    create_activity,
    get_activity,
    get_topic_activities
)


initialize_database()


activity_id = create_activity(
    topic_id="6cf2d123-9153-4812-aebe-b5312d7ad5bb",
    topic="Funções",
    learning_objective="Resolver problemas envolvendo funções",
    activity_type="multiple_choice",
    difficulty=2,
    cognitive_skill="aplicação prática",
    learning_dimension="aplicar",
    question="Uma corrida custa R$4 fixos mais R$2 por km. Qual função representa?",
    options=[
        "P(x)=2x+4",
        "P(x)=4x+2",
        "P(x)=6x",
        "P(x)=4/x"
    ],
    correct_answer="P(x)=2x+4",
    explanation="A taxa fixa é o termo independente e o valor por km multiplica a distância.",
    hints=[
        "Observe a taxa fixa.",
        "Veja qual valor acompanha x.",
        "Monte a função do primeiro grau."
    ]
)


print("ID atividade:")
print(activity_id)


print("\nBusca:")
print(
    get_activity(activity_id)
)


print("\nPor tópico:")
for activity in get_topic_activities(
    "6cf2d123-9153-4812-aebe-b5312d7ad5bb"
):
    print(activity)