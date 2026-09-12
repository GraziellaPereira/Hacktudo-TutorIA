import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from app.model.learning_material import LearningMaterial


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_learning_material(
    content,
    student,
    topic
):
    if isinstance(topic, str):
        topic_name = topic
        topic_description = ""
        topic_learning_objectives = []
        topic_concepts = []
        topic_practical_applications = []
    else:
        topic_name = topic.name
        topic_description = topic.description
        topic_learning_objectives = topic.learning_objectives
        topic_concepts = topic.concepts
        topic_practical_applications = topic.practical_applications

    prompt = f"""

Você é um especialista em aprendizagem personalizada.

Transforme o conteúdo abaixo em um material
de estudo adaptado para o aluno.

Aluno:

Nível:
{student.education_level}

Ano:
{student.grade_or_period}

Método escolhido:
{student.preferred_method}


REGRAS GERAIS:

- Utilize exclusivamente o conteúdo fornecido.
- Não crie conceitos que não estejam presentes no conteúdo.
- Não adicione classificações, propriedades, exemplos ou aplicações externas.
- Antes de retornar, compare cada item com o conteúdo original e remova
    qualquer informação que não possa ser apoiada por ele.
- Adapte a linguagem ao nível educacional do aluno.
- Retorne somente JSON válido.
- Não inclua markdown.
- Não inclua comentários fora do JSON.

Se o método for flashcards:

- gere entre 8 e 12 flashcards;
- cada flashcard deve possuir um id único;
- varie entre compreensão, aplicação e análise;
- não use somente perguntas iniciadas por "O que é";
- inclua situações práticas quando o conteúdo permitir;
- a dica deve ajudar o raciocínio sem revelar a resposta;
- a resposta deve ser curta e objetiva;
- informe a dificuldade entre 1 e 5;
- informe o conceito relacionado;
- não repita perguntas equivalentes.

Se o método for mapa mental:

- crie uma estrutura hierárquica com pelo menos três nós;
- o primeiro nó deve ser o conceito central;
- o nó central deve possuir `level: 0`;
- cada filho deve possuir `level` igual ao nível do pai mais 1;
- use children para representar conceitos relacionados;
- coloque objetos MindMapNode completos em children;
- nunca use strings ou apenas IDs em children;
- retorne connections com source, target e type para cada relação;
- source e target devem corresponder aos ids dos nós existentes;
- cada nó deve possuir entre 2 e 6 palavras-chave;
- use títulos específicos, como "Domínio e Saída", "Representação Gráfica",
  "Função Afim" ou "Função Quadrática"; evite títulos genéricos como
  "Conjuntos", "Tópicos" ou "Propriedades";
- cada nó deve possuir um resumo curto de uma ou duas frases;
- diferencie conceitos principais, secundários e relações;
- use concepts para listar ideias associadas ao nó;
- cubra os conceitos centrais e os tópicos realmente presentes no conteúdo;
- não substitua os tópicos do conteúdo por classificações não mencionadas;
- não escreva parágrafos longos.

Se o método for infográfico:

- crie pelo menos três seções curtas e independentes;
- cada seção deve possuir título, texto de no máximo 240 caracteres
    e entre 2 e 5 pontos-chave;
- escreva textos objetivos, próprios para leitura rápida;
- destaque definições, relações, exemplos ou aplicações importantes;
- cubra somente informações presentes no conteúdo original;
- não descreva cores, fontes ou componentes visuais;
- retorne apenas o conteúdo semântico que o frontend deve apresentar.


Nome do tópico:
{topic_name}

Descrição:
{topic_description}

Objetivos:
{topic_learning_objectives}

Conceitos:
{topic_concepts}

Aplicações:
{topic_practical_applications}


Retorne somente JSON.

CHECKLIST FINAL:
- cada item está apoiado pelo conteúdo original;
- nenhum conceito externo foi introduzido;
- o mapa mental representa relações reais entre os conceitos;
- o infográfico contém pelo menos três seções curtas e complementares;
- não há conteúdo repetido ou contraditório.
- Revise os espaços entre palavras e após pontuação antes de retornar.
- Não una palavras por erro de formatação.
"""


    ultimo_erro = None

    for attempt in range(3):
        instrucoes = prompt
        if ultimo_erro is not None:
            instrucoes += f"""

ATENÇÃO: a resposta anterior foi rejeitada.
O método escolhido é "{student.preferred_method}".
Retorne obrigatoriamente o conteúdo desse método preenchido.
Para flashcards, retorne entre 8 e 12 objetos em `flashcards`.
Para mind_map, retorne pelo menos três nós hierárquicos, com palavras-chave,
resumo e relações em `children`, sempre como objetos completos.
Inclua `connections` com source, target e type para representar as relações.
Inclua `level: 0` no nó central e incremente o level em cada descendente.
Para infographic, retorne pelo menos três seções com textos curtos e pontos-chave.
Não deixe a lista correspondente ao método vazia.
"""

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=instrucoes,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LearningMaterial,
                ),
            )

            if not response.text:
                raise RuntimeError("A API não retornou material.")

            material = LearningMaterial.model_validate_json(response.text)
            if material.method != student.preferred_method:
                raise ValueError(
                    "O método retornado é diferente do método escolhido."
                )

            return material
        except (ValidationError, ValueError) as error:
            ultimo_erro = error
            if attempt == 2:
                raise RuntimeError(
                    "A API retornou material inválido após 3 tentativas."
                ) from error

    raise RuntimeError("Não foi possível gerar o material.")
    