from app.services.activity_service import generate_activities
from app.services.validator_service import validate_activity
from app.model.content import Topic

from app.storage.activity_repository import (
    create_activity,
    mark_activity_regenerated
)


def regenerate_activity(
    old_activity,
    context,
    topic
):
    if isinstance(topic, dict):
        topic = Topic.model_validate(topic)

    old_question = " ".join(
        old_activity["question"].casefold().split()
    )
    validation_errors = []

    for _ in range(3):
        activities = generate_activities(context, topic)

        for new_activity in activities.activities:
            new_question = " ".join(
                new_activity.question.casefold().split()
            )

            if new_question == old_question:
                validation_errors.append("A IA repetiu a questão anterior.")
                continue

            validation = validate_activity(new_activity)
            if not validation.approved:
                validation_errors.extend(validation.errors)
                continue

            mark_activity_regenerated(old_activity["id"])

            return create_activity(
                topic_id=old_activity["topic_id"],
                topic=old_activity["topic"],
                learning_objective=new_activity.learning_objective,
                activity_type=new_activity.type,
                difficulty=new_activity.difficulty,
                cognitive_skill=new_activity.cognitive_skill,
                learning_dimension=new_activity.learning_dimension,
                question=new_activity.question,
                options=new_activity.options,
                correct_answer=new_activity.correct_answer,
                explanation=new_activity.explanation,
                hints=new_activity.hints,
                review_status="pending",
                validation_score=validation.score,
                validation_warnings=validation.warnings,
                regenerated_from=old_activity["id"],
            )

    reasons = "; ".join(dict.fromkeys(validation_errors))
    raise ValueError(
        "Não foi possível gerar nova questão aprovada. "
        f"Motivos: {reasons or 'nenhuma questão diferente foi retornada.'}"
    )