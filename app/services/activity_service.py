import os
import time
from uuid import uuid4

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.model.activity import ActivitySet


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY não foi encontrada no arquivo .env")

client = genai.Client(api_key=api_key)




def generate_activities(context, topic):


    prompt = f"""
Você é um professor especialista em criação de avaliações adaptativas
para diferentes níveis educacionais.

Sua tarefa é criar atividades de aprendizagem personalizadas com base
no conteúdo fornecido.

O público pode variar entre:
- ensino fundamental;
- ensino médio;
- ensino técnico;
- graduação;
- treinamentos profissionais.

Adapte:
- linguagem;
- complexidade;
- exemplos;
- profundidade;
- contexto das questões;

de acordo com o nível educacional informado.

OBJETIVO:

Avaliar se o aluno realmente compreendeu o conteúdo,
consegue aplicar o conhecimento e resolver situações relacionadas.

As questões devem priorizar aprendizagem e raciocínio,
não apenas memorização.

REGRAS:

1. Cada questão deve estar vinculada a um objetivo de aprendizagem específico.

2. Distribua os tipos de questões:

30%:
- compreensão de conceitos;
- identificação de ideias principais.

50%:
- aplicação prática;
- resolução de problemas;
- tomada de decisão;
- interpretação de situações.

20%:
- análise;
- comparação;
- avaliação crítica;
- criação de soluções.

3. Evite perguntas puramente decorativas.

Não utilize:

- "O que é X?"
- "Defina X."
- "Qual é a definição de X?"

Quando possível, prefira:

- situações reais;
- estudos de caso;
- exemplos do cotidiano;
- problemas profissionais;
- análise de cenários.

4. Adapte o formato ao conteúdo.

Exemplos:

Matemática:
- resolução de problemas;
- interpretação de cálculos.

História:
- análise de eventos;
- comparação de períodos.

Biologia:
- interpretação de fenômenos;
- aplicação em situações reais.

Programação:
- análise de código;
- previsão de resultados;
- identificação de erros.

Administração:
- tomada de decisão;
- análise de cenários.

5. As alternativas devem:

- possuir apenas uma resposta correta;
- apresentar erros comuns dos alunos;
- ser plausíveis;
- não entregar a resposta pelo tamanho ou formato.
- gere exatamente 4 alternativas para cada questão;
- informe em `correct_answer` o texto exato da alternativa correta.

Antes de retornar, faça uma revisão final de cada questão:
- confirme que existem exatamente 4 alternativas diferentes;
- confirme que `correct_answer` é idêntico ao texto de uma alternativa;
- resolva novamente o problema para confirmar que há apenas uma alternativa correta;
- confira se a explicação justifica a resposta sem contradizê-la;
- remova qualquer questão ambígua, incompleta ou com dados insuficientes.

6. As dicas devem funcionar como um tutor:

Primeira dica:
- relembra o conceito.

Segunda dica:
- direciona o raciocínio.

Terceira dica:
- aproxima o aluno da solução.

Nunca revele diretamente a resposta.

7. A explicação deve:

- justificar a resposta correta;
- explicar o raciocínio utilizado;
- mostrar o conceito aplicado.

8. Antes de retornar, valide:

- a questão está relacionada ao objetivo de aprendizagem?
- exige algum tipo de raciocínio?
- está adequada ao nível do aluno?
- existe apenas uma resposta correta?

9. Gere pelo menos 5 questões para este tópico.

Diversifique a dificuldade das questões:
- inclua pelo menos uma questão fácil (dificuldade 1 ou 2);
- inclua pelo menos uma questão média (dificuldade 3);
- inclua pelo menos uma questão difícil (dificuldade 4 ou 5);
- distribua as demais questões entre esses níveis, evitando repetir sempre
  a mesma dificuldade.

Use dificuldade 1 para compreensão básica, 2 para aplicação simples,
3 para aplicação prática, 4 para análise e resolução de problemas e
5 para avaliação crítica ou criação de soluções.

Quando o conteúdo possuir uma linguagem, ferramenta ou tecnologia específica,
utilize exclusivamente essa tecnologia nas atividades.

Não substitua exemplos por tecnologias diferentes.

O professor pode fornecer focos específicos de avaliação.

Caso sejam informados:
- priorize esses pontos na criação das atividades.

Caso não sejam informados:
- identifique automaticamente os principais aspectos que devem ser avaliados com base no conteúdo e objetivo de aprendizagem.

Antes de retornar, revise cada questão. se for matemática, recalcule a resposta correta, se for outra disciplina, verifique a coerência do conteúdo.

A resposta correta deve ser recalculada.
A explicação final deve ser limpa e definitiva.
Nunca mencione erros, recálculos ou tentativas de correção.
Não escreva frases como "Aguarde", "recalculando" ou "vamos ajustar".
Não altere a questão dentro da explicação.
Use somente conceitos presentes no conteúdo fornecido.

A atividade será revisada por um professor antes de ser disponibilizada aos alunos.

O campo review_status deve sempre iniciar como "pending".

Os campos validation_score, validation_warnings e teacher_modified
devem iniciar vazios ou com valores padrão.

Nunca altere uma atividade já aprovada ou editada pelo professor.

Para cada questão, informe learning_dimension usando exatamente uma destas categorias:

- concept: compreensão de um conceito;
- relationship: relação entre conceitos;
- specific_information: lembrança de informação específica;
- application: aplicação do conhecimento em uma situação;
- interpretation: interpretação de texto, gráfico, tabela ou cenário.

Escolha a categoria que melhor representa a habilidade principal avaliada.

Retorne exclusivamente JSON válido.

Conteúdo analisado:

Disciplina:
{context.subject}

Nível educacional:
{context.education_level}

Ano/Semestre:
{context.grade_or_period}

Público-alvo:
{context.target_audience}

Objetivo de aprendizagem geral:
{context.learning_goal}

Focos específicos da avaliação:
{context.assessment_focus or "Nenhum foco específico informado."}

Tópico:
{topic.name}

Descrição:
{topic.description}

Objetivos de aprendizagem:
{topic.learning_objectives}

Conceitos:
{topic.concepts}

Aplicações práticas:
{topic.practical_applications}


Formato obrigatório:

{{
  "activities": [
    {{
  "topic": "",
  "learning_objective": "",
  "type": "multiple_choice",
  "difficulty": 1,
  "cognitive_skill": "",
  "question": "",
  "options": [
    "",
    "",
    "",
    ""
  ],
  "correct_answer": "",
  "explanation": "",
  "hints": [
    "",
    "",
    ""
  ],
  "review_status": "pending",
  "validation_score": null,
  "validation_warnings": [],
  "teacher_modified": false,
  "learning_dimension": ""
    }}
  ]
}}
"""


    ultimo_erro = None

    for attempt in range(3):
      try:
        instrucoes = prompt
        if ultimo_erro is not None:
          instrucoes += """

  ATENÇÃO: o lote anterior foi rejeitado na validação.
  Garanta que `correct_answer` seja exatamente igual ao texto de uma das
  quatro alternativas correspondentes.
  """

        response = client.models.generate_content(
          model="gemini-3.5-flash-lite",
          contents=instrucoes,
          config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ActivitySet,
          ),
        )

        if not response.text:
          raise RuntimeError("A API não retornou atividades.")

        activity_set = ActivitySet.model_validate_json(response.text)
        for activity in activity_set.activities:
          activity.activity_id = str(uuid4())

        return activity_set
      except errors.ServerError:
        if attempt == 2:
          raise
        time.sleep(2 ** attempt)
      except ValidationError as error:
        ultimo_erro = error
        if attempt == 2:
          raise RuntimeError(
            "A API retornou atividades inválidas após 3 tentativas."
          ) from error
        time.sleep(2 ** attempt)

    raise RuntimeError("Não foi possível gerar atividades.")