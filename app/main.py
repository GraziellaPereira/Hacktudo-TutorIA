from app.services.llm_service import analyze_content
from app.services.activity_service import generate_activities
from app.services.validator_service import validate_activity
from app.model.context import LearningContext
from app.services.learning_method_service import generate_learning_material
from app.services.summary_service import generate_summary
from app.services.performance_service import (
    calculate_accuracy,
    calculate_error_profile,
    has_improved,
    has_mastered,
    recommend_method,
    register_attempt,
    select_activity_batch,
)
from app.model.student import StudentContext


aluno = StudentContext(

    student_id="001",

    education_level="Ensino Médio",

    grade_or_period="3º ano",

    preferred_method=None,

)


texto = """
Funções são relações que associam cada elemento de um conjunto de entrada,
chamado domínio, a um único elemento de um conjunto de saída. Em uma função
real, a variável independente geralmente é representada por x e a variável
dependente por f(x). O gráfico de uma função é formado pelos pontos (x, f(x))
no plano cartesiano e permite analisar seu comportamento, como crescimento,
decrescimento, zeros e valores máximos ou mínimos.

As funções afim e linear podem ser escritas como f(x) = ax + b. O coeficiente
a representa a taxa de variação: quando a é positivo, a função é crescente;
quando a é negativo, é decrescente. O termo b indica o valor de f(0), ou seja,
o ponto em que o gráfico cruza o eixo y.

As funções quadráticas têm a forma f(x) = ax² + bx + c, com a diferente de
zero, e seu gráfico é uma parábola. Se a é positivo, a parábola possui um
ponto de mínimo; se a é negativo, possui um ponto de máximo.
"""


def estudar_conteudo(texto, aluno, topic_name, incluir_resumo=True):
    print("\n==============================")
    print("CONTEÚDO ORIGINAL DO PROFESSOR")
    print("==============================")
    print(texto)

    escolha = input(
        "\nDeseja gerar um material de estudo com a IA? (s/n): "
    ).strip().casefold()

    if escolha != "s":
        print("Você seguirá apenas com o conteúdo original do professor.")
        return None

    if incluir_resumo:
        resumo = generate_summary(
            texto,
            aluno,
        )

        print("\n==============================")
        print("RESUMO GERADO PELA IA")
        print("==============================")
        print(resumo.model_dump_json(indent=2))

        input(
            "\nDigite ENTER quando terminar o resumo para receber o material: "
        )

    if aluno.preferred_method is None:
        print(
            "\nO método será recomendado após as questões diagnósticas."
        )
        return None

    material = generate_learning_material(
        texto,
        aluno,
        topic_name,
    )

    print("\n==============================")
    print(f"MATERIAL DE ESTUDO: {aluno.preferred_method}")
    print("==============================")
    print(material.model_dump_json(indent=2))
    return material


estudar_conteudo(
    texto,
    aluno,
    "Funções",
)


contexto = LearningContext(
    subject="Matemática",
    education_level="Ensino Médio",
    grade_or_period="3º ano",
    target_audience="Alunos preparando ENEM",
    learning_goal="Resolver problemas envolvendo funções",
    assessment_focus=[
        "interpretação de gráficos",
        "resolução de problemas"
    ]
)



def preparar_atividade(atividade, validacao):

    atividade.review_status = "pending"

    atividade.validation_score = validacao.score

    atividade.validation_warnings = validacao.warnings

    atividade.teacher_modified = False

    return atividade



def gerar_questoes(contexto, topico, quantidade=3):

    questoes = []


    while len(questoes) < quantidade:

        atividades = generate_activities(
            contexto,
            topico
        )


        for atividade in atividades.activities:

            validacao = validate_activity(
                atividade
            )


            if not validacao.approved:
                continue


            atividade = preparar_atividade(
                atividade,
                validacao
            )


            questoes.append(
                atividade
            )


            if len(questoes) == quantidade:
                break


    return questoes



def regenerar_questao(
    contexto,
    topico,
    questao_antiga,
    tentativas=3
):

    pergunta_antiga = " ".join(
        questao_antiga.question.casefold().split()
    )


    for _ in range(tentativas):

        atividades = generate_activities(
            contexto,
            topico
        )


        for nova in atividades.activities:

            pergunta_nova = " ".join(
                nova.question.casefold().split()
            )


            if pergunta_nova == pergunta_antiga:
                continue


            validacao = validate_activity(
                nova
            )


            if validacao.approved:

                return preparar_atividade(
                    nova,
                    validacao
                )


    raise RuntimeError(
        "Não foi possível gerar nova questão."
    )



def editar_questao(questao):

    print("\n========== EDITAR QUESTÃO ==========")


    questao.question = input(
        "\nNova pergunta:\n"
    )


    print("\nInforme as 4 alternativas:")

    novas_alternativas = []


    for i in range(4):

        alternativa = input(
            f"Alternativa {i+1}: "
        )

        novas_alternativas.append(
            alternativa
        )


    questao.options = novas_alternativas


    questao.correct_answer = input(
        "\nNova resposta correta:\n"
    )


    alterar_explicacao = input(
        "\nAlterar explicação? (s/n): "
    )


    if alterar_explicacao.lower() == "s":

        questao.explanation = input(
            "Nova explicação:\n"
        )


    alterar_dicas = input(
        "\nAlterar dicas? (s/n): "
    )


    if alterar_dicas.lower() == "s":

        novas_dicas = []


        for i in range(3):

            dica = input(
                f"Dica {i+1}: "
            )

            novas_dicas.append(
                dica
            )


        questao.hints = novas_dicas


    validacao = validate_activity(
        questao
    )


    if not validacao.approved:
        print(
            "\n⚠️ A edição precisa de ajustes antes de ser salva."
        )

        print(
            "A questão retornará para revisão."
        )

        print(
            "\nProblemas encontrados:"
        )

        for erro in validacao.errors:
            print("-", erro)

        questao.review_status = "pending"
        return questao

    questao.teacher_modified = True
    questao.review_status = "edited"
    questao.validation_score = validacao.score
    questao.validation_warnings = validacao.warnings

    print(
        "\n✏️ Questão editada pelo professor."
    )

    return questao



def revisar_professor(
    questao,
    contexto,
    topico
):

    while True:

        print("\n==============================")
        print("REVISÃO DO PROFESSOR")
        print("==============================")


        print(
            "Status:",
            questao.review_status
        )


        print(
            "Nota IA:",
            questao.validation_score
        )


        if questao.validation_warnings:

            print("\nAvisos:")

            for aviso in questao.validation_warnings:

                print("-", aviso)



        print("\nPergunta:")
        print(
            questao.question
        )


        print("\nAlternativas:")

        for i, opcao in enumerate(
            questao.options,
            start=1
        ):

            print(
                f"{i}. {opcao}"
            )


        print("\nResposta:")
        print(
            questao.correct_answer
        )


        print("\nAções:")
        print("[1] Aprovar")
        print("[2] Editar")
        print("[3] Gerar nova questão")


        escolha = input("> ")



        if escolha == "1":

            questao.review_status = "approved"

            print(
                "\n✅ Questão aprovada pelo professor."
            )

            return questao


        elif escolha == "2":

            return editar_questao(
                questao
            )



        elif escolha == "3":
            print(
                "\n🔄 Gerando nova questão..."
            )

            nova = regenerar_questao(
                contexto,
                topico,
                questao
            )

            print(
                "\n✅ Nova questão gerada."
            )

            print(
                "Aguardando nova aprovação do professor."
            )

            return nova


        else:

            print(
                "Opção inválida."
            )


def aplicar_quiz(aluno, atividades, tentativas, quantidade, method=None):
    ids_respondidos = {
        tentativa.activity_id
        for tentativa in tentativas
    }

    lote = select_activity_batch(
        activities=atividades,
        answered_ids=ids_respondidos,
        batch_size=quantidade
    )

    if not lote:
        raise RuntimeError("Não há questões disponíveis para o quiz.")

    if quantidade is not None and len(lote) < quantidade:
        raise RuntimeError(
            f"São necessárias {quantidade} questões, mas só há "
            f"{len(lote)} disponíveis."
        )

    print("\n==============================")
    print(f"QUIZ - método: {method or 'diagnóstico'}")
    print("==============================")

    for indice, atividade in enumerate(lote, start=1):
        print(f"\nQuestão {indice}: {atividade.question}")
        for opcao_indice, opcao in enumerate(atividade.options, start=1):
            print(f"  {opcao_indice}. {opcao}")

        resposta = input("Resposta: ").strip()
        if resposta.isdigit() and 1 <= int(resposta) <= len(atividade.options):
            resposta = atividade.options[int(resposta) - 1]

        tentativa = register_attempt(
            student_id=aluno.student_id,
            activity=atividade,
            method=method,
            selected_answer=resposta,
        )
        tentativas.append(tentativa)

        resultado = "correta" if tentativa.is_correct else "incorreta"
        print(f"Resposta {resultado}.")

    return lote



conteudo = analyze_content(
    texto,
    contexto
)


questoes_finais = []


total_esperado = len(conteudo.topics) * 5



for topico in conteudo.topics:

    print("\n==============================")
    print("TÓPICO:", topico.name)
    print("==============================")


    questoes = gerar_questoes(
        contexto,
        topico,
        quantidade=5
    )


    for questao in questoes:


        while True:

            resultado = revisar_professor(
                questao,
                contexto,
                topico
            )


            if resultado.review_status == "pending":

                questao = resultado

                continue


            break



        questoes_finais.append(
            resultado
        )



print("\n==============================")
print("RESULTADO FINAL")
print("==============================")


aprovadas = [
    q for q in questoes_finais
    if q.review_status in [
        "approved",
        "edited"
    ]
]


if len(aprovadas) == total_esperado:

    print(
        "Todas as questões foram aprovadas."
    )

    print(
        f"{len(aprovadas)} questões liberadas para alunos."
    )

    print("\nResumo:")

    for q in aprovadas:

        print(
            f"- {q.topic}: {q.review_status}"
        )


else:

    print(
        "Ainda existem questões pendentes."
    )


    print(
        f"{len(aprovadas)}/{total_esperado} aprovadas."
    )


if aprovadas:
    tentativas_diagnosticas = []
    quantidade_diagnostico = 10

    aplicar_quiz(
        aluno,
        aprovadas,
        tentativas_diagnosticas,
        quantidade=quantidade_diagnostico,
        method=None,
    )

    perfil_erros = calculate_error_profile(tentativas_diagnosticas)
    aluno.preferred_method = recommend_method(
        error_profile=perfil_erros,
        used_methods=set(),
    )

    print("\n==============================")
    print("DIAGNÓSTICO INICIAL")
    print("==============================")
    print(f"Acurácia: {calculate_accuracy(tentativas_diagnosticas):.0%}")
    print(f"Perfil de erros: {dict(perfil_erros)}")
    print(f"Método recomendado: {aluno.preferred_method}")

    tentativas_anteriores = tentativas_diagnosticas
    metodos_usados = set()

    while aluno.preferred_method is not None:
        metodo_atual = aluno.preferred_method
        metodos_usados.add(metodo_atual)

        estudar_conteudo(
            texto,
            aluno,
            topico,
            incluir_resumo=False,
        )
        input(
            "\nDigite ENTER quando terminar este método para iniciar as questões: "
        )

        tentativas_metodo = []
        aplicar_quiz(
            aluno,
            aprovadas,
            tentativas_metodo,
            quantidade=None,
            method=metodo_atual,
        )

        acuracia_metodo = calculate_accuracy(tentativas_metodo)
        perfil_metodo = calculate_error_profile(tentativas_metodo)

        print("\n==============================")
        print(f"RESULTADO DO MÉTODO: {metodo_atual}")
        print("==============================")
        print(f"Acurácia da etapa: {acuracia_metodo:.0%}")
        print(f"Perfil de erros: {dict(perfil_metodo)}")

        if has_improved(tentativas_anteriores, tentativas_metodo):
            print("O desempenho melhorou em relação à etapa anterior.")
        else:
            print("O desempenho ainda não apresentou melhora suficiente.")

        todas_tentativas = tentativas_diagnosticas + tentativas_metodo
        if has_mastered(todas_tentativas):
            print("Domínio demonstrado. O estudo foi finalizado.")
            break

        proximo_metodo = recommend_method(
            error_profile=perfil_metodo,
            used_methods=metodos_usados,
        )

        if proximo_metodo is None:
            print("Os três métodos foram concluídos.")
            break

        tentativas_anteriores = tentativas_metodo
        aluno.preferred_method = proximo_metodo
        print(f"Próximo método recomendado: {proximo_metodo}")

