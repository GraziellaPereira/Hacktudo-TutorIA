from app.database.database import initialize_database
from app.storage.topic_repository import (
    create_topic,
    get_topic,
    get_content_topics
)


initialize_database()


topic_id = create_topic(
    content_id="89d4d538-4a40-43b5-927e-cdd89892acb2",
    name="Funções",
    description="Estudo de funções matemáticas.",
    importance=5,
    difficulty=3,
    learning_objectives=[
        "Resolver problemas envolvendo funções"
    ],
    concepts=[
        "Domínio",
        "Imagem",
        "Gráficos"
    ],
    practical_applications=[
        "Problemas do cotidiano"
    ]
)


print("ID tópico:")
print(topic_id)



print("\nBusca individual:")

topic = get_topic(topic_id)

print(topic)



print("\nBusca por conteúdo:")

topics = get_content_topics(
    "89d4d538-4a40-43b5-927e-cdd89892acb2"
)

for t in topics:
    print(t)