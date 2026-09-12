from app.services.llm_service import analyze_content
from app.services.activity_service import generate_activities
from app.services.validator_service import validate_activity

from app.storage.content_repository import create_content
from app.storage.topic_repository import create_topic
from app.storage.activity_repository import create_activity



def process_teacher_content(
    teacher_id,
    title,
    text,
    context
):

    # ==========================
    # 1 - Salvar conteúdo original
    # ==========================

    content_id = create_content(
        teacher_id=teacher_id,
        title=title,
        original_text=text
    )


    # ==========================
    # 2 - Analisar conteúdo com IA
    # ==========================

    analyzed_content = analyze_content(
        text,
        context
    )


    total_topics = 0
    total_activities = 0


    # ==========================
    # 3 - Salvar tópicos
    # ==========================

    for topic in analyzed_content.topics:

        topic_id = create_topic(

            content_id=content_id,

            name=topic.name,

            description=topic.description,

            importance=topic.importance,

            difficulty=topic.difficulty,

            learning_objectives=topic.learning_objectives,

            concepts=topic.concepts,

            practical_applications=topic.practical_applications

        )


        total_topics += 1



        # ==========================
        # 4 - Gerar atividades
        # ==========================

        activities = generate_activities(
            context,
            topic
        )


        # ==========================
        # 5 - Validar e salvar
        # ==========================

        for activity in activities.activities:


            validation = validate_activity(
                activity
            )


            create_activity(

                topic_id=topic_id,

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

                teacher_modified=False

            )


            total_activities += 1



    return {

        "content_id": content_id,

        "topics_created": total_topics,

        "activities_created": total_activities

    }