import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.model.learning_material import LearningSummary


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_summary(content, student):
    prompt = f"""
Você é um especialista em educação.

Crie um resumo didático e fiel do conteúdo fornecido pelo professor.

Regras:
- utilize exclusivamente o conteúdo fornecido;
- adapte a linguagem ao nível do aluno;
- destaque os conceitos e relações mais importantes;
- não inclua informações externas;
- não crie atividades, flashcards ou perguntas;
- retorne somente JSON válido.

Nível educacional:
{student.education_level}

Ano:
{student.grade_or_period}

Conteúdo original:
{content}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LearningSummary,
        ),
    )

    if not response.text:
        raise RuntimeError("A API não retornou um resumo.")

    return LearningSummary.model_validate_json(response.text)
