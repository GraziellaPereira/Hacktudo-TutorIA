from app.model.content import Topic
from app.model.student import StudentContext
from app.services.learning_method_service import generate_learning_material


CONTENT = """
Funções são relações que associam cada elemento de um conjunto de entrada,
chamado domínio, a um único elemento de um conjunto de saída. Em uma função
real, a variável independente é representada por x e a variável dependente
por f(x). O gráfico é formado pelos pontos (x, f(x)) no plano cartesiano.

As funções afim e linear podem ser escritas como f(x) = ax + b. O coeficiente
a representa a taxa de variação: quando a é positivo, a função é crescente;
quando a é negativo, é decrescente. O termo b indica o valor de f(0), o ponto
em que o gráfico cruza o eixo y.

As funções quadráticas têm a forma f(x) = ax² + bx + c, com a diferente de
zero, e seu gráfico é uma parábola. Se a é positivo, possui um ponto de
mínimo; se a é negativo, possui um ponto de máximo.
"""


TOPIC = Topic(
    name="Funções",
    description=(
        "Relações entre domínio e saída, com representação gráfica e estudo "
        "das funções afim, linear e quadrática."
    ),
    importance=5,
    difficulty=3,
    learning_objectives=[
        "Interpretar o domínio e a saída de uma função.",
        "Analisar o crescimento e o decrescimento de funções afim e linear.",
        "Identificar máximo, mínimo e parábola em funções quadráticas.",
    ],
    concepts=[
        "domínio",
        "saída",
        "gráfico no plano cartesiano",
        "função afim",
        "função linear",
        "coeficientes a e b",
        "função quadrática",
        "parábola",
        "máximo e mínimo",
    ],
    practical_applications=[
        "Interpretar gráficos de situações cotidianas.",
        "Analisar crescimento, decrescimento, máximos e mínimos.",
    ],
)


for method in ("mind_map", "infographic"):
    student = StudentContext(
        student_id="test-001",
        education_level="Ensino Medio",
        grade_or_period="3o ano",
        preferred_method=method,
    )

    material = generate_learning_material(
        CONTENT,
        student,
        TOPIC,
    )

    print("\n==============================")
    print(f"METODO: {method}")
    print("==============================")
    print(material.model_dump_json(indent=2))
