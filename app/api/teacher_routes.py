from fastapi import APIRouter, UploadFile, File, Form

from app.services.teacher_service import process_teacher_content
from app.model.context import LearningContext
from app.services.file_service import extract_text

from pathlib import Path
import shutil


router = APIRouter(
    prefix="/teachers",
    tags=["Professor"]
)


@router.post("/{teacher_id}/contents")
def create_teacher_content(

    teacher_id: str,

    title: str = Form(...),

    subject: str = Form(...),

    education_level: str = Form(...),

    grade_or_period: str = Form(...),

    target_audience: str = Form(...),

    learning_goal: str = Form(...),

    assessment_focus: list[str] = Form([]),

    file: UploadFile = File(...)

):

    # ===============================
    # Salvar arquivo temporariamente
    # ===============================

    temp_path = Path(
        "temp"
    ) / file.filename


    temp_path.parent.mkdir(
        exist_ok=True
    )


    with open(temp_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # ===============================
    # Extrair texto PDF/PPTX
    # ===============================

    text = extract_text(
        str(temp_path)
    )


    # ===============================
    # Criar contexto da IA
    # ===============================

    context = LearningContext(

        subject=subject,

        education_level=education_level,

        grade_or_period=grade_or_period,

        target_audience=target_audience,

        learning_goal=learning_goal,

        assessment_focus=assessment_focus

    )


    # ===============================
    # Processar conteúdo
    # ===============================

    result = process_teacher_content(

        teacher_id,

        title,

        text,

        context

    )


    return result