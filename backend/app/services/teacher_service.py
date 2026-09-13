from app.services.llm_service import analyze_content
from app.services.activity_service import generate_activities
from app.services.validator_service import validate_activity
from app.model.content import Topic
from app.storage.content_repository import create_content, update_content_summary
from app.storage.topic_repository import create_topic, get_content_topics
from app.storage.activity_repository import create_activity, get_content_activities



def process_teacher_content(
    teacher_id,
    title,
    text,
    context,
    context_id=None,
    classroom_id=None,
    subject_id=None,
    attachment_path=None,
    attachment_name=None,
):
    content_id = create_content(
        teacher_id=teacher_id,
        title=title,
        original_text=text,
        context=context,
        context_id=context_id,
        classroom_id=classroom_id,
        subject_id=subject_id,
        attachment_path=attachment_path,
        attachment_name=attachment_name,
    )

    analyzed_content = analyze_content(text, context)
    update_content_summary(content_id, analyzed_content.summary)

    for topic in analyzed_content.topics:
        create_topic(
            content_id=content_id,
            description=topic.description,
            name=topic.name,
            importance=topic.importance,
            difficulty=topic.difficulty,
            learning_objectives=topic.learning_objectives,
            concepts=topic.concepts,
            practical_applications=topic.practical_applications,
        )

    return {
        "content_id": content_id,
        "topics_created": len(analyzed_content.topics),
        "analysis": analyzed_content.model_dump(),
    }


def generate_content_activities(content_id, context):
    existing_activities = get_content_activities(content_id)
    if existing_activities:
        return existing_activities

    generated_activities = []
    for topic_data in get_content_topics(content_id):
        topic = Topic.model_validate(topic_data)
        activity_set = generate_activities(context, topic)

        for activity in activity_set.activities:
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
                review_status="pending",
                validation_score=validation.score,
                validation_warnings=validation.warnings,
            )
            generated_activity = activity.model_dump()
            generated_activity.pop("activity_id", None)
            generated_activity["id"] = activity_id
            generated_activities.append(generated_activity)

    return generated_activities