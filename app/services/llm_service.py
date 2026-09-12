import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import ValidationError
from app.model.content import ContentAnalysis

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY não foi encontrada no arquivo .env")

client = genai.Client(api_key=api_key)

def analyze_content(content, context) -> ContentAnalysis:
    prompt = f"""
Você é um especialista em educação, didática e análise de conteúdos.

Sua tarefa é analisar o material fornecido por um professor e transformá-lo
em uma estrutura de conhecimento que possa ser utilizada para criar uma
experiência de aprendizagem personalizada.

Analise cuidadosamente o conteúdo enviado.

Identifique:

- título do conteúdo;
- resumo geral;
- disciplina ou área de conhecimento relacionada;
- nível educacional adequado;
- faixa etária estimada;
- tópicos principais;
- descrição de cada tópico;
- importância de cada tópico para o aprendizado;
- dificuldade estimada;
- objetivos de aprendizagem;
- conceitos fundamentais;
- aplicações práticas;
- possíveis pré-requisitos;
- habilidades desenvolvidas.

REGRAS IMPORTANTES:

1. Utilize EXCLUSIVAMENTE as informações presentes no conteúdo enviado.

2. Não invente informações que não estejam presentes.

3. Caso alguma informação não possa ser identificada com segurança,
utilize valores genéricos ou deixe a informação vazia.

4. O nível educacional e o objetivo pedagógico serão fornecidos pelo professor.
Utilize essas informações para adaptar:
- linguagem;
- complexidade;
- exemplos;
- profundidade;
- tipo de atividade.

5. Os objetivos de aprendizagem devem representar aquilo que o aluno
será capaz de fazer após estudar o conteúdo.

Exemplos:
- compreender um conceito;
- resolver um problema;
- aplicar uma técnica;
- interpretar informações;
- comparar ideias;
- criar uma solução.

6. A importância deve representar o impacto daquele tópico no aprendizado:

5 = conceito essencial para compreender o restante do conteúdo.
4 = conceito muito relevante.
3 = conceito importante, mas não fundamental.
2 = conceito complementar.
1 = conceito adicional.

7. A dificuldade deve representar o esforço cognitivo necessário:

1 = compreensão básica.
2 = aplicação simples.
3 = aplicação em situações práticas.
4 = análise e resolução de problemas.
5 = domínio avançado ou criação.

8. Identifique aplicações práticas sempre que possível.

Exemplos:
- matemática: resolver problemas reais;
- história: interpretar acontecimentos;
- biologia: relacionar conceitos com situações da vida;
- programação: criar ou analisar soluções;
- administração: tomar decisões.

Retorne exclusivamente JSON válido.
Não utilize markdown.
Não escreva explicações fora do JSON.

Identifique todos os tópicos relevantes presentes no conteúdo.

Retorne no mínimo 3 tópicos distintos, desde que existam informações
suficientes no conteúdo para descrevê-los. Não agrupe conceitos diferentes
em um único tópico apenas para reduzir a quantidade.

Não agrupe assuntos diferentes em um único tópico.

Cada conceito principal deve ser representado como um tópico separado quando possuir objetivos de aprendizagem próprios.

O conteúdo analisado pode pertencer a qualquer área do conhecimento.
Não presuma que o aluno possui conhecimento prévio.
A análise deve focar nos conceitos e habilidades presentes no material.

Contexto educacional:

Disciplina:
{context.subject}

Nível:
{context.education_level}

Ano/Semestre:
{context.grade_or_period}

Público:
{context.target_audience}

Objetivo:
{context.learning_goal}

Utilize o contexto educacional informado para interpretar o conteúdo.

O objetivo do professor deve influenciar:
- quais conceitos são mais importantes;
- quais habilidades devem ser priorizadas;
- qual profundidade deve ser considerada;
- como se comunicar com o aluno;
- quais exemplos e aplicações práticas devem ser utilizados.

Conteúdo:

{content}
"""


    ultimo_erro = None

    for attempt in range(3):
        instrucoes = prompt
        if ultimo_erro is not None:
            instrucoes += """

ATENÇÃO: a análise anterior foi rejeitada porque retornou menos de 3 tópicos
ou tópicos inválidos. Gere novamente no mínimo 3 tópicos distintos, usando
somente informações presentes no conteúdo.
"""

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=instrucoes,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ContentAnalysis,
                ),
            )
            if not response.text:
                raise RuntimeError("A API não retornou uma análise.")

            return ContentAnalysis.model_validate_json(response.text)
        except errors.ServerError:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
        except ValidationError as error:
            ultimo_erro = error
            if attempt == 2:
                raise RuntimeError(
                    "A API retornou uma análise inválida após 3 tentativas."
                ) from error
            time.sleep(2 ** attempt)

    raise RuntimeError("Não foi possível analisar o conteúdo.")