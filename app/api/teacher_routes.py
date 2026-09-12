from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from pathlib import Path
import shutil


from app.services.teacher_service import process_teacher_content

from app.model.context import LearningContext

from app.services.file_service import extract_text


from app.storage.content_repository import (
    get_content
)

from app.storage.topic_repository import (
    get_content_topics
)

from app.storage.activity_repository import (
    get_content_activities,
    get_pending_activities_by_content,
    get_activity,
    update_activity_review
)


from app.api.schemas import (
    ActivityReviewRequest
)



router = APIRouter(
    prefix="/teachers",
    tags=["Professor"]
)



# ==================================================
# Criar conteúdo pelo professor
# ==================================================

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


    with open(
        temp_path,
        "wb"
    ) as buffer:

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





# ==================================================
# Buscar conteúdo completo
# ==================================================

@router.get("/contents/{content_id}")
def teacher_content(

    content_id: str

):

    return {

        "content": get_content(
            content_id
        ),

        "topics": get_content_topics(
            content_id
        ),

        "activities": get_content_activities(
            content_id
        )

    }





# ==================================================
# Buscar questões pendentes de revisão
# ==================================================

@router.get(
    "/contents/{content_id}/activities/pending"
)
def pending_activities(

    content_id: str

):

    return get_pending_activities_by_content(

        content_id

    )





# ==================================================
# Aprovar / editar questão
# ==================================================

@router.patch(
    "/activities/{activity_id}/review"
)
def review_activity(

    activity_id: str,

    review: ActivityReviewRequest

):


    activity = get_activity(

        activity_id

    )


    if not activity:

        raise HTTPException(

            status_code=404,

            detail="Atividade não encontrada"

        )


    update_activity_review(

        activity_id,

        review.review_status,

        review.teacher_modified,

        review.question,

        review.options,

        review.correct_answer,

        review.explanation,

        review.hints

    )


    return {

        "message": "Revisão atualizada",

        "activity_id": activity_id,

        "status": review.review_status

    }