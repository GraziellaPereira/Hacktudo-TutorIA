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
    process_teacher_content,
    generate_content_activities,
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
from app.storage.content_repository import get_teacher_contents
from app.database.database import connection_scope


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

from app.storage.student_content_repository import (
    create_student_content
)


from app.api.schemas import (
    ActivityReviewRequest,
    ContextCreateRequest,
    ContextStructureUpdateRequest,
    TeacherCreateRequest,
)


from app.services.regenerate_service import (
    regenerate_activity
)

from app.storage.teacher_repository import (
    create_teacher,
    get_teacher,
    get_teachers,
)

from app.storage.context_repository import create_context, update_context_structure


router = APIRouter(
    prefix="/teachers",
    tags=["Professor"]
)


@router.post("")
def create_teacher_route(data: TeacherCreateRequest):
    teacher_id = create_teacher(
        name=data.name,
        description=data.description,
        email=data.email,
    )
    return {"teacher_id": teacher_id}


@router.get("")
def list_teachers():
    return get_teachers()


@router.get("/{teacher_id}")
def teacher_profile(teacher_id: str):
    teacher = get_teacher(teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado",
        )
    return teacher


@router.post("/{teacher_id}/contexts")
def create_teacher_context(teacher_id: str, data: ContextCreateRequest):
    if not get_teacher(teacher_id):
        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado",
        )

    context = create_context(
        teacher_id=teacher_id,
        name=data.name,
        description=data.description,
    )
    context["classrooms"] = []
    context["subjects"] = []
    return context


@router.put("/{teacher_id}/contexts/{context_id}")
def update_teacher_context(
    teacher_id: str,
    context_id: str,
    data: ContextStructureUpdateRequest,
):
    if not get_teacher(teacher_id):
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    context = update_context_structure(context_id, data.classrooms, data.subjects)
    if not context or context["teacher_id"] != teacher_id:
        raise HTTPException(status_code=404, detail="Contexto não encontrado")

    return context


# ==================================================
# Criar conteúdo pelo professor
# ==================================================

@router.get("/{teacher_id}/contents")
def list_teacher_contents(teacher_id: str):
    if not get_teacher(teacher_id):
        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado",
        )

    return get_teacher_contents(teacher_id)

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

    if not get_teacher(teacher_id):
        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado",
        )


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

@router.get("/contents/{content_id}/analysis")
def content_analysis(content_id: str):
    content = get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")

    topics = get_content_topics(content_id)
    learning_objectives = []
    concepts = []
    for topic in topics:
        learning_objectives.extend(topic["learning_objectives"])
        concepts.extend(topic["concepts"])

    return {
        "content_id": content_id,
        "title": content["title"],
        "summary": content.get("summary") or "",
        "review_status": content.get("review_status", "pending"),
        "topics": topics,
        "learning_objectives": list(dict.fromkeys(learning_objectives)),
        "concepts": list(dict.fromkeys(concepts)),
        "activities": get_content_activities(content_id),
    }


@router.post("/contents/{content_id}/approve")
def approve_content(content_id: str):
    content = get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")

    context = get_content_context(content_id)
    activities = generate_content_activities(content_id, context)

    with connection_scope() as connection:
        connection.execute(
            "UPDATE contents SET review_status = 'approved' WHERE id = ?",
            (content_id,),
        )

    return {
        **content_analysis(content_id),
        "activities": activities,
    }

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

@router.post(
    "/contents/{content_id}/students/{student_id}"
)
def assign_content_to_student(

    content_id: str,

    student_id: str

):

    relation_id = create_student_content(

        student_id,

        content_id

    )


    return {

        "message":
        "Conteúdo vinculado ao aluno",

        "relation_id":
        relation_id

    }