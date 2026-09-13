def classify_learning_problem(concept: str):

    concept_mapping = {

        "Domínio": "concept",

        "Conjunto de saída": "concept",

        "Plano cartesiano": "relationship",

        "Gráfico": "interpretation",

    }


    return concept_mapping.get(
        concept,
        "concept"
    )



def recommend_method(
    error_profile,
    used_methods=None,
    performance=None,
):

    used_methods = used_methods or set()


    mapping = {

        "concept": "flashcards",

        "relationship": "mind_map",

        "specific_information": "infographic",

        "application": "flashcards",

        "interpretation": "mind_map",

    }


    if not error_profile:
        return "flashcards"


    ordered_errors = sorted(
        error_profile.items(),
        key=lambda item:item[1],
        reverse=True
    )


    for concept, _ in ordered_errors:
        problem_type = next(
            (
                item.get("learning_dimension")
                for item in performance or []
                if item.get("concept") == concept
            ),
            classify_learning_problem(concept),
        )


        method = mapping[problem_type]


        if method not in used_methods:

            return method


    return "flashcards"