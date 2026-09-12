from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from pathlib import Path
import shutil


from app.services.teacher_service import (
    process_teacher_content
)

from app.model.context import (
    LearningContext
)

from app.services.file_service import (
    extract_text
)


from app.storage.content_repository import (
    get_content,
    get_content_context
)


from app.storage.topic_repository import (
    get_content_topics,
    get_topic
)


from app.storage.activity_repository import (
    get_content_activities,
    get_pending_activities_by_content,
    get_approved_activities_by_content,
    get_activity,
    update_activity_review
)


from app.api.schemas import (
    ActivityReviewRequest
)


from app.services.regenerate_service import (
    regenerate_activity
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


    text = extract_text(
        str(temp_path)
    )


    context = LearningContext(

        subject=subject,

        education_level=education_level,

        grade_or_period=grade_or_period,

        target_audience=target_audience,

        learning_goal=learning_goal,

        assessment_focus=assessment_focus

    )


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
# Questões pendentes
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

        "message":
        "Revisão atualizada",

        "activity_id":
        activity_id,

        "status":
        review.review_status

    }



# ==================================================
# Questões aprovadas
# ==================================================

@router.get(
    "/contents/{content_id}/activities/approved"
)
def approved_activities(

    content_id: str

):

    return get_approved_activities_by_content(
        content_id
    )



# ==================================================
# Regenerar questão pela IA
# ==================================================

@router.post(
    "/activities/{activity_id}/regenerate/{content_id}"
)
def regenerate_question(

    activity_id: str,

    content_id: str

):


    activity = get_activity(
        activity_id
    )


    if not activity:

        raise HTTPException(

            status_code=404,

            detail="Atividade não encontrada"

        )


    # busca contexto original usado pelo professor

    content_context = get_content_context(
        content_id
    )


    if not content_context:

        raise HTTPException(

            status_code=404,

            detail="Contexto do conteúdo não encontrado"

        )


    # busca tópico

    topic = get_topic(
        activity["topic_id"]
    )


    if not topic:

        raise HTTPException(

            status_code=404,

            detail="Tópico não encontrado"

        )



    try:
        new_id = regenerate_activity(
            activity,
            content_context,
            topic
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error


    return {

        "message":

        "Questão regenerada com sucesso",

        "old_activity":

        activity_id,

        "new_activity":

        new_id

    }