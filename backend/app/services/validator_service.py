from app.model.validation import ActivityValidation
from app.model.activity import Activity


def _normalize(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def validate_activity(activity: Activity) -> ActivityValidation:
    errors = []
    warnings = []
    score = 100

    if len(activity.options) != 4:
        errors.append("A questão deve possuir exatamente 4 alternativas.")

    normalized_options = [_normalize(option) for option in activity.options]
    if any(not option for option in normalized_options):
        errors.append("As alternativas não podem estar vazias.")
    if len(set(normalized_options)) != len(normalized_options):
        errors.append("As alternativas não podem ser repetidas.")
    if _normalize(activity.correct_answer) not in normalized_options:
        errors.append("A resposta correta não está presente nas alternativas.")

    required_fields = {
        "tópico": activity.topic,
        "objetivo de aprendizagem": activity.learning_objective,
        "tipo": activity.type,
        "habilidade cognitiva": activity.cognitive_skill,
        "pergunta": activity.question,
        "resposta correta": activity.correct_answer,
        "explicação": activity.explanation,
    }
    for field_name, value in required_fields.items():
        if not value.strip():
            errors.append(f"O campo {field_name} não pode estar vazio.")

    if activity.type != "multiple_choice":
        errors.append("O tipo da atividade deve ser 'multiple_choice'.")

    if len(activity.hints) != 3:
        errors.append("A questão deve possuir exatamente 3 dicas.")
    elif any(not hint.strip() for hint in activity.hints):
        errors.append("As dicas não podem estar vazias.")

    if len(activity.explanation.strip()) < 30:
        warnings.append(
            "A explicação parece muito curta."
        )

    if len(activity.question.strip()) < 20:
        warnings.append("A pergunta parece curta demais para avaliar raciocínio.")

    searchable_text = _normalize(
        " ".join(
            [
                activity.question,
                activity.explanation,
                *activity.options,
                *activity.hints,
            ]
        )
    )
    forbidden_phrases = (
        "aguarde",
        "recalculando",
        "vamos ajustar",
        "houve um erro",
        "erro no gabarito",
        "opção correta gerada",
        "vamos corrigir",
    )
    for phrase in forbidden_phrases:
        if phrase in searchable_text:
            errors.append(
                "A atividade contém texto do processo de revisão da IA."
            )
            break

    normalized_answer = _normalize(activity.correct_answer)
    if normalized_answer and any(
        normalized_answer in _normalize(hint) for hint in activity.hints
    ):
        warnings.append("Uma dica pode estar revelando diretamente a resposta.")

    score = max(0, 100 - (30 * len(errors)) - (10 * len(warnings)))
    approved = not errors and score >= 80


    return ActivityValidation(
        approved=approved,
        score=max(score, 0),
        errors=errors,
        warnings=warnings
    )

def validate_learning_material(material):
    errors = []

    if not material.title.strip():
        errors.append("O título não pode estar vazio.")

    if not material.summary.strip():
        errors.append("O resumo não pode estar vazio.")

    if material.method == "flashcards":
        if len(material.flashcards) < 8:
            errors.append(
                "O material deve possuir pelo menos 8 flashcards."
            )

        ids = [card.id for card in material.flashcards]
        if len(ids) != len(set(ids)):
            errors.append("Os flashcards devem possuir ids únicos.")

        questions = [
            " ".join(card.question.casefold().split())
            for card in material.flashcards
        ]
        if len(questions) != len(set(questions)):
            errors.append("Existem flashcards repetidos.")

        for card in material.flashcards:
            if card.hint.casefold().strip() == card.answer.casefold().strip():
                errors.append(
                    f"A dica do flashcard {card.id} revela diretamente a resposta."
                )

    return errors