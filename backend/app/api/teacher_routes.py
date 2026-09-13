from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)
from fastapi.responses import FileResponse

from pathlib import Path
import shutil
import sqlite3
import uuid


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
    get_content_context,
    update_content,
)
from app.storage.content_repository import get_teacher_contents
from app.database.database import connection_scope


from app.storage.topic_repository import (
    get_content_topics,
    get_topic,
    update_topic,
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
    ContentUpdateRequest,
    TeacherCreateRequest,
    TeacherUpdateRequest,
)


from app.services.regenerate_service import (
    regenerate_activity
)

from app.storage.teacher_repository import (
    create_teacher,
    get_teacher,
    get_teachers,
    update_teacher,
)

from app.storage.context_repository import (
    add_context_subject,
    create_context,
    get_teacher_contexts,
    update_context_structure,
    update_context_subject,
)


router = APIRouter(
    prefix="/teachers",
    tags=["Professor"]
)

ATTACHMENT_ROOT = Path(__file__).resolve().parents[2] / "data" / "attachments"


@router.post("")
def create_teacher_route(data: TeacherCreateRequest):
    try:
        teacher_id = create_teacher(
            name=data.name,
            description=data.description,
            email=data.email or None,
        )
    except sqlite3.IntegrityError as error:
        if "teachers.email" in str(error):
            raise HTTPException(
                status_code=409,
                detail="Este e-mail já está cadastrado.",
            ) from error
        raise

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


@router.put("/{teacher_id}")
def update_teacher_profile(teacher_id: str, data: TeacherUpdateRequest):
    if data.name is not None and not data.name.strip():
        raise HTTPException(status_code=422, detail="O nome não pode ficar vazio")

    teacher = update_teacher(
        teacher_id,
        name=data.name,
        description=data.description,
        email=data.email,
    )
    if not teacher:
        raise HTTPException(status_code=404, detail="Professor não encontrado")

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


@router.get("/{teacher_id}/subjects")
def list_teacher_subjects(teacher_id: str):
    if not get_teacher(teacher_id):
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    subjects = []
    seen_ids = set()
    for context in get_teacher_contexts(teacher_id):
        for subject in context.get("subjects", []):
            subject_id = str(subject.get("id"))
            if subject_id not in seen_ids:
                subjects.append(subject)
                seen_ids.add(subject_id)
        for classroom in context.get("classrooms", []):
            for subject in classroom.get("subjects", []):
                subject_id = str(subject.get("id"))
                if subject_id not in seen_ids:
                    subjects.append(subject)
                    seen_ids.add(subject_id)

    return subjects


@router.post("/{teacher_id}/contexts/{context_id}/subjects")
def create_teacher_subject(teacher_id: str, context_id: str, data: dict):
    if not get_teacher(teacher_id):
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    context = next(
        (item for item in get_teacher_contexts(teacher_id) if item["id"] == context_id),
        None,
    )
    if not context:
        raise HTTPException(status_code=404, detail="Contexto não encontrado")

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise HTTPException(status_code=400, detail="Nome da matéria é obrigatório")

    subject = {
        "id": str(uuid.uuid4()),
        "contextId": context_id,
        "name": name.strip(),
        "description": data.get("description", ""),
        "importanceLevel": data.get("importanceLevel", "Medium"),
        "classrooms": data.get("classrooms", []),
        "files": data.get(
            "files",
            {"pdf": 0, "videos": 0, "audios": 0, "powerpoint": 0},
        ),
        "activities": data.get("activities", []),
    }
    updated_context = add_context_subject(context_id, subject)
    if not updated_context:
        raise HTTPException(status_code=404, detail="Contexto não encontrado")

    return subject


@router.put("/{teacher_id}/contexts/{context_id}/subjects/{subject_id}")
def update_teacher_subject(
    teacher_id: str,
    context_id: str,
    subject_id: str,
    data: dict,
):
    if not get_teacher(teacher_id):
        raise HTTPException(status_code=404, detail="Professor não encontrado")

    context = next(
        (item for item in get_teacher_contexts(teacher_id) if item["id"] == context_id),
        None,
    )
    if not context:
        raise HTTPException(status_code=404, detail="Contexto não encontrado")

    updated_context = update_context_subject(
        context_id,
        subject_id,
        data.get("classrooms", []),
    )
    if not updated_context:
        raise HTTPException(status_code=404, detail="Matéria não encontrada")

    for subject in updated_context.get("subjects", []):
        if str(subject.get("id")) == subject_id:
            return subject
    for classroom in updated_context.get("classrooms", []):
        for subject in classroom.get("subjects", []):
            if str(subject.get("id")) == subject_id:
                return subject

    raise HTTPException(status_code=404, detail="Matéria não encontrada")


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

    contents = get_teacher_contents(teacher_id)
    for content in contents:
        content.pop("original_text", None)
        content.pop("attachment_path", None)
    return contents

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

    context_id: str | None = Form(None),

    classroom_id: str | None = Form(None),

    subject_id: str | None = Form(None),

    file: UploadFile = File(...)

):

    if not get_teacher(teacher_id):
        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado",
        )


    original_filename = file.filename or "anexo"
    attachment_path = ATTACHMENT_ROOT / f"{uuid.uuid4()}{Path(original_filename).suffix.lower()}"
    attachment_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = Path("temp") / f"{uuid.uuid4()}{Path(original_filename).suffix.lower()}"


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

        context,
        context_id=context_id,
        classroom_id=classroom_id,
        subject_id=subject_id,
        attachment_path=str(attachment_path),
        attachment_name=original_filename,

    )

    shutil.copyfile(temp_path, attachment_path)
    temp_path.unlink(missing_ok=True)


    return result


@router.get("/contents/{content_id}/attachment")
def download_content_attachment(content_id: str):
    content = get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")

    attachment_path = content.get("attachment_path")
    if not attachment_path or not Path(attachment_path).is_file():
        raise HTTPException(status_code=404, detail="Anexo não encontrado")

    return FileResponse(
        attachment_path,
        filename=content.get("attachment_name") or Path(attachment_path).name,
    )



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

    public_content = dict(content)
    public_content.pop("original_text", None)

    return {
        "content_id": content_id,
        "title": public_content["title"],
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

    public_content = get_content(content_id)
    if not public_content:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
    public_content.pop("original_text", None)

    return {

        "content": public_content,

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

    if review.options is not None:
        if len(review.options) != 4 or len(set(review.options)) != 4:
            raise HTTPException(
                status_code=422,
                detail="A atividade deve possuir exatamente 4 alternativas diferentes",
            )
        effective_correct_answer = review.correct_answer or activity["correct_answer"]
        if effective_correct_answer not in review.options:
            raise HTTPException(
                status_code=422,
                detail="A resposta correta deve estar entre as alternativas",
            )

    if review.hints is not None and len(review.hints) != 3:
        raise HTTPException(
            status_code=422,
            detail="A atividade deve possuir exatamente 3 dicas",
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

        "id":
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


@router.patch("/contents/{content_id}")
def update_teacher_content(content_id: str, data: ContentUpdateRequest):
    content = get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")

    if data.title is not None and not data.title.strip():
        raise HTTPException(status_code=422, detail="O título não pode ficar vazio")

    update_content(
        content_id,
        data.title.strip() if data.title is not None else None,
        data.summary.strip() if data.summary is not None else None,
    )

    if data.topics is not None:
        existing_topics = {
            topic["id"]: topic
            for topic in get_content_topics(content_id)
        }
        for topic in data.topics:
            if topic.id not in existing_topics:
                raise HTTPException(status_code=422, detail="Tópico inválido")
            update_topic(
                topic.id,
                topic.name.strip(),
                topic.description.strip(),
                topic.learning_objectives,
                topic.concepts,
                topic.practical_applications,
            )

    return content_analysis(content_id)