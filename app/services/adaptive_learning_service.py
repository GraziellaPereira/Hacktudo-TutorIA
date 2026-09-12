from app.services.recommendation_service import recommend_method
from app.services.learning_method_service import generate_learning_material
from app.storage.recommendation_repository import create_recommendation


def _calculate_overall_performance(performance):
    total_attempts = sum(item["attempts"] for item in performance)
    total_correct = sum(item["correct_answers"] for item in performance)
    accuracy = total_correct / total_attempts if total_attempts else 0

    return total_attempts, accuracy


def _classify_learning_state(performance):
    total_attempts, accuracy = _calculate_overall_performance(performance)
    has_review_concept = any(
        item["error_rate"] >= 0.5
        for item in performance
    )

    if (
        total_attempts >= 20
        and accuracy >= 0.95
        and all(item["error_rate"] <= 0.1 for item in performance)
    ):
        return "completed"

    if total_attempts >= 10 and accuracy >= 0.8 and not has_review_concept:
        return "mastered"

    if has_review_concept:
        return "needs_review"

    return "practicing"


def _build_state_response(
    recommendation_id,
    status,
    action,
    error_profile,
    method,
    reason,
    material=None,
):
    response = {
        "recommendation_id": recommendation_id,
        "status": status,
        "action": action,
        "identified_problems": error_profile,
        "recommended_method": method,
        "reason": reason,
        "material": material,
    }

    if status == "completed":
        response["message"] = "Você dominou este conteúdo."
        response["next_step"] = "Avançar para o próximo tópico"

    return response



def generate_adaptive_material(

    student,

    content,

    topic,

    performance,

    content_id=None,

):

    if isinstance(content, dict):
        content_id = content["id"]
        content_text = content["original_text"]
    else:
        content_text = content

    error_profile = {}


    for item in performance:

        if item["error_rate"] > 0:

            error_profile[item["concept"]] = (
                item["error_rate"]
            )

    status = _classify_learning_state(performance)

    if status == "completed":
        recommendation_id = create_recommendation(
            student.student_id,
            content_id,
            status,
            "advance",
            None,
            "O aluno consolidou o conteúdo com desempenho consistente.",
        )
        return _build_state_response(
            recommendation_id,
            status,
            "advance",
            error_profile,
            None,
            "O aluno consolidou o conteúdo com desempenho consistente.",
        )

    if status == "needs_review":
        reason = "O aluno ainda apresenta dificuldade conceitual."
    elif status == "mastered":
        reason = "O aluno domina os conceitos e pode avançar para um desafio."
    else:
        reason = "O aluno compreendeu parcialmente e precisa consolidar o conteúdo."

    focus_concepts = [
        item["concept"]
        for item in performance
        if item["error_rate"] > 0
    ]

    if status == "mastered" and not focus_concepts:
        focus_concepts = [item["concept"] for item in performance]

    method = "flashcards" if status == "mastered" else recommend_method(
        error_profile
    )

    if status == "needs_review" and method == "flashcards":
        method = "mind_map"

    student.preferred_method = method

    material = generate_learning_material(
        content_text,
        student,
        topic,
        focus_concepts=focus_concepts,
    )

    recommendation_id = create_recommendation(
        student.student_id,
        content_id,
        status,
        "generate_material",
        method,
        reason,
    )

    return _build_state_response(
        recommendation_id,
        status,
        "generate_material",
        error_profile,
        method,
        reason,
        material,
    )