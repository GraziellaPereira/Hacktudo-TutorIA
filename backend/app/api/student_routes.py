import json

from fastapi import APIRouter, HTTPException
from google.genai import errors

from app.api.schemas import StudentCreateRequest

from app.model.content import Topic
from app.model.activity import Activity
from app.model.student import StudentContext

from app.storage.student_repository import (
    create_student,
    get_student,
    get_students
)

from app.storage.student_content_repository import (
    create_student_content,
    get_student_contents
)

from app.storage.activity_repository import get_approved_activities_by_content

from app.storage.content_repository import (
    get_content,
    get_content_context,
    update_content_summary
)

from app.storage.topic_repository import (
    get_content_topics
)

from app.storage.recommendation_repository import (
    get_student_recommendations
)

from app.storage.learning_method_repository import (
    get_learning_methods
)

from app.storage.learning_material_repository import (
    create_learning_material,
    get_learning_materials
)

from app.storage.student_learning_preference_repository import (
    save_preference,
    get_preference
)

from app.services.summary_service import (
    generate_summary
)

from app.services.learning_method_service import (
    generate_learning_material
)

from app.services.activity_service import (
    ASSESSMENT_ACTIVITY_COUNT,
    generate_activities,
)
from app.services.validator_service import validate_activity
from app.storage.activity_repository import create_activity

from app.storage.student_attempt_repository import (
    create_attempt,
    get_student_attempts,
)

from app.storage.performance_repository import (
    get_student_performance_by_concept
)

from app.services.adaptive_learning_service import (
    generate_adaptive_material
)

from app.services.performance_service import select_activity_batch

from app.storage.performance_repository import (
    get_student_performance_by_concept
)

from app.storage.topic_repository import (
    get_content_topics
)

router = APIRouter(
    prefix="/students",
    tags=["Aluno"]
)


def _assessment_batch(activities, answered_ids=None):
    answered_ids = answered_ids or set()
    models = []
    for activity in activities:
        payload = dict(activity)
        payload["activity_id"] = payload["id"]
        models.append(Activity.model_validate(payload))

    selected = select_activity_batch(
        models,
        answered_ids=answered_ids,
        batch_size=ASSESSMENT_ACTIVITY_COUNT,
    )
    result = []
    for activity in selected:
        payload = activity.model_dump()
        payload["id"] = payload.pop("activity_id")
        result.append(payload)
    return result

def _generate_adaptive_batch(content, topic_data):
    context = get_content_context(content["id"])
    topic = Topic.model_validate(topic_data)
    activity_set = generate_activities(context, topic)
    batch = []

    for activity in activity_set.activities[:ASSESSMENT_ACTIVITY_COUNT]:
        validation = validate_activity(activity)
        activity_id = create_activity(
            topic_id=topic_data["id"],
            topic=activity.topic,
            learning_objective=activity.learning_objective,
            activity_type=activity.type,
            difficulty=activity.difficulty,
            cognitive_skill=activity.cognitive_skill,
            learning_dimension=activity.learning_dimension,
            question=activity.question,
            options=activity.options,
            correct_answer=activity.correct_answer,
            explanation=activity.explanation,
            hints=activity.hints,
            review_status="approved",
            validation_score=validation.score,
            validation_warnings=validation.warnings,
        )
        payload = activity.model_dump()
        payload.pop("activity_id", None)
        payload["id"] = activity_id
        batch.append(payload)

    return batch


# ==================================================
# Métodos de aprendizagem disponíveis
# ==================================================

@router.get("/learning-methods")
def learning_methods():

    return get_learning_methods()



# ==================================================
# Criar aluno
# ==================================================

@router.post("")
def create_student_route(
    data: StudentCreateRequest
):

    student_id = create_student(
        name=data.name,
        education_level=data.education_level,
        grade_or_period=data.grade_or_period
    )

    return {
        "student_id": student_id
    }



# ==================================================
# Listar alunos
# ==================================================

@router.get("")
def list_students():

    return get_students()



# ==================================================
# Buscar conteúdos do aluno
# ==================================================

@router.get("/{student_id}/contents")
def student_contents(
    student_id: str
):

    student = get_student(
        student_id
    )


    if not student:

        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado"
        )


    return get_student_contents(
        student_id
    )


@router.post("/{student_id}/contents/{content_id}")
def add_student_content(student_id: str, content_id: str):
    if not get_student(student_id):
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    content = get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")

    if content.get("review_status") != "approved":
        raise HTTPException(
            status_code=409,
            detail="Este conteúdo ainda não foi publicado pelo professor",
        )

    if any(item["id"] == content_id for item in get_student_contents(student_id)):
        return content

    create_student_content(student_id, content_id)
    return content


@router.get("/{student_id}/contents/{content_id}")
def student_content_detail(student_id: str, content_id: str):
    if not get_student(student_id):
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    if not any(item["id"] == content_id for item in get_student_contents(student_id)):
        raise HTTPException(status_code=403, detail="Aluno não possui acesso a este conteúdo")

    content = get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Conteúdo não encontrado")

    approved_activities = get_approved_activities_by_content(content_id)
    answered_ids = {
        attempt["item_id"]
        for attempt in get_student_attempts(student_id)
        if attempt["item_type"] == "activity"
    }
    assessment_activities = _assessment_batch(approved_activities, answered_ids)

    student_content = dict(content)
    student_content.pop("original_text", None)
    student_content.pop("attachment_path", None)
    attachment_name = student_content.pop("attachment_name", None)
    student_content["attachment_name"] = attachment_name
    student_content["has_attachment"] = bool(attachment_name)

    return {
        "content": student_content,
        "topics": get_content_topics(content_id),
        "activities": assessment_activities,
        "assessment": {
            "total": len(assessment_activities),
            "available": len(approved_activities),
            "selection_size": ASSESSMENT_ACTIVITY_COUNT,
        },
    }

# ==================================================
# Gerar / consultar resumo do conteúdo
# ==================================================

@router.post(
    "/{student_id}/contents/{content_id}/summary"
)
def create_summary(
    student_id: str,
    content_id: str
):

    student = get_student(
        student_id
    )


    if not student:

        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado"
        )


    content = get_content(
        content_id
    )


    if not content:

        raise HTTPException(
            status_code=404,
            detail="Conteúdo não encontrado"
        )


    # =====================================
    # Verificar acesso do aluno ao conteúdo
    # =====================================

    student_contents = get_student_contents(
        student_id
    )


    has_access = any(
        item["id"] == content_id
        for item in student_contents
    )


    if not has_access:

        raise HTTPException(
            status_code=403,
            detail="Aluno não possui acesso a este conteúdo"
        )



    # =====================================
    # Verificar método escolhido
    # =====================================

    preference = get_preference(
        student_id,
        content_id
    )


    if not preference:

        raise HTTPException(
            status_code=400,
            detail="Aluno ainda não escolheu método de aprendizagem"
        )



    student_context = StudentContext(

        student_id=student["id"],

        education_level=
        student["education_level"],

        grade_or_period=
        student["grade_or_period"],

        preferred_method=
        preference["preferred_method"]

    )



    # =====================================
    # Retorna resumo existente
    # =====================================

    if content.get("summary"):

        try:

            saved_summary = json.loads(
                content["summary"]
            )

        except json.JSONDecodeError:

            saved_summary = {
                "summary": content["summary"]
            }


        return {

            "summary": saved_summary,

            "generated": False

        }



    # =====================================
    # Gerar resumo IA
    # =====================================

    summary = generate_summary(

        content["original_text"],

        student_context

    )



    update_content_summary(

        content_id,

        summary.model_dump()

    )



    return {

        "summary": summary,

        "generated": True

    }



# ==================================================
# Escolher método de aprendizagem
# ==================================================

@router.post(
    "/{student_id}/contents/{content_id}/method"
)
def select_learning_method(

    student_id: str,

    content_id: str,

    data: dict

):

    student = get_student(
        student_id
    )


    if not student:

        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado"
        )



    content = get_content(
        content_id
    )


    if not content:

        raise HTTPException(
            status_code=404,
            detail="Conteúdo não encontrado"
        )



    method = data.get(
        "method"
    )


    allowed_methods = [

        "flashcards",

        "mind_map",

        "infographic"

    ]



    if method not in allowed_methods:

        raise HTTPException(

            status_code=400,

            detail="Método inválido"

        )



    preference_id = save_preference(

        student_id,

        content_id,

        None,

        method

    )



    return {

        "message": "Método salvo",

        "preference_id": preference_id,

        "method": method

    }

# ==================================================
# Gerar material de aprendizagem
# Usa o método salvo pelo aluno
# ==================================================

@router.post(
    "/{student_id}/contents/{content_id}/materials"
)
def create_learning_material_route(

    student_id: str,

    content_id: str

):

    student = get_student(
        student_id
    )


    if not student:

        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado"
        )



    content = get_content(
        content_id
    )


    if not content:

        raise HTTPException(
            status_code=404,
            detail="Conteúdo não encontrado"
        )



    # =====================================
    # Buscar método escolhido pelo aluno
    # =====================================

    preference = get_preference(

        student_id,

        content_id

    )


    if not preference:

        raise HTTPException(
            status_code=400,
            detail="Aluno ainda não escolheu método de aprendizagem"
        )



    method = preference["preferred_method"]



    # =====================================
    # Buscar tópicos do conteúdo
    # =====================================

    topics = get_content_topics(

        content_id

    )


    if not topics:

        raise HTTPException(
            status_code=400,
            detail="Conteúdo sem tópicos"
        )



    topic = Topic.model_validate(

        topics[0]

    )



    # =====================================
    # Criar contexto do aluno
    # =====================================

    student_context = StudentContext(

        student_id=student["id"],

        education_level=
        student["education_level"],

        grade_or_period=
        student["grade_or_period"],

        preferred_method=method

    )



    # =====================================
    # Gerar material IA
    # =====================================

    material = generate_learning_material(

        content["original_text"],

        student_context,

        topic

    )



    # =====================================
    # Salvar material
    # =====================================

    material_id = create_learning_material(

        student_id,

        content_id,

        topics[0]["id"],

        method,

        material.model_dump()

    )



    return {

        "id": material_id,

        "method": method,

        "material": material

    }



# ==================================================
# Listar materiais gerados do aluno
# ==================================================

@router.get(
    "/{student_id}/contents/{content_id}/materials"
)
def student_learning_materials(

    student_id: str,

    content_id: str

):

    student = get_student(

        student_id

    )


    if not student:

        raise HTTPException(

            status_code=404,

            detail="Aluno não encontrado"

        )



    return get_learning_materials(

        student_id,

        content_id

    )



# ==================================================
# Consultar método escolhido
# ==================================================

@router.get(
    "/{student_id}/contents/{content_id}/method"
)
def get_learning_method(

    student_id: str,

    content_id: str

):

    preference = get_preference(

        student_id,

        content_id

    )


    if not preference:

        raise HTTPException(

            status_code=404,

            detail="Método ainda não escolhido"

        )


    return preference



# ==================================================
# Buscar perfil do aluno
# Deixar sempre por último
# ==================================================

@router.get("/{student_id}")
def student_profile(

    student_id: str

):

    student = get_student(

        student_id

    )


    if not student:

        raise HTTPException(

            status_code=404,

            detail="Aluno não encontrado"

        )


    return student

@router.post(
    "/{student_id}/materials/{material_id}/attempt"
)
def register_attempt(

    student_id: str,

    material_id: str,

    data: dict

):

    attempt_id = create_attempt(

        student_id,

        material_id,

        data["item_id"],

        data["item_type"],

        data.get(
            "concept"
        ),

        data["correct"],

        data.get(
            "response_time_seconds",
            0
        )

    )


    return {

        "message":
        "Resposta registrada",

        "attempt_id":
        attempt_id

    }

@router.get(
    "/{student_id}/performance"
)
def student_performance(
    student_id: str
):

    student = get_student(
        student_id
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado"
        )


    return get_student_performance_by_concept(
        student_id
    )

@router.post(
    "/{student_id}/contents/{content_id}/adaptive"
)
def adaptive_learning(
    student_id: str,
    content_id: str
):

    student = get_student(
        student_id
    )

    if not student:
        raise HTTPException(
            404,
            "Aluno não encontrado"
        )


    content = get_content(
        content_id
    )

    if not content:
        raise HTTPException(
            404,
            "Conteúdo não encontrado"
        )


    topics = get_content_topics(
        content_id
    )

    if not topics:
        raise HTTPException(
            status_code=400,
            detail="Conteúdo sem tópicos"
        )

    topic = Topic.model_validate(
        topics[0]
    )


    performance = get_student_performance_by_concept(
        student_id
    )


    student_context = StudentContext(
        student_id=student["id"],
        education_level=student["education_level"],
        grade_or_period=student["grade_or_period"],
        preferred_method=None
    )


    result = generate_adaptive_material(
        student_context,
        content,
        topic,
        performance
    )

    material = result.get("material")
    save_preference(student_id, content_id, None, result["recommended_method"])
    if material is not None:
        material_payload = material.model_dump()
        material_id = create_learning_material(
            student_id,
            content_id,
            topics[0]["id"],
            result["recommended_method"],
            material_payload,
        )
        result["material_id"] = material_id
        result["material"] = material_payload

    approved_activities = get_approved_activities_by_content(content_id)
    answered_ids = {
        attempt["item_id"]
        for attempt in get_student_attempts(student_id)
        if attempt["item_type"] == "activity"
    }
    next_batch = []
    if result["accuracy"] < 0.8:
        try:
            next_batch = _generate_adaptive_batch(content, topics[0])
        except errors.ServerError:
            result["assessment_error"] = (
                "O método foi recomendado, mas a IA está temporariamente indisponível "
                "para gerar o próximo lote de questões."
            )
    result["assessment"] = {
        "activities": next_batch,
        "total": len(next_batch),
        "selection_size": ASSESSMENT_ACTIVITY_COUNT,
        "continue": result["accuracy"] < 0.8 and bool(next_batch),
    }
    return result


@router.get(
    "/{student_id}/contents/{content_id}/recommendations"
)
def recommendations_history(
    student_id: str,
    content_id: str
):

    return get_student_recommendations(
        student_id,
        content_id
    )