import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

import app.database.database as database
from app.api.app import app
from app.model.context import LearningContext
from app.model.learning_material import Flashcard, LearningMaterial
from app.storage.content_repository import create_content
from app.storage.recommendation_repository import create_recommendation
from app.storage.student_content_repository import create_student_content
from app.storage.topic_repository import create_topic


class ApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        )
        cls.original_database_path = database.DATABASE_PATH
        database.DATABASE_PATH = Path(cls.temp_dir.name) / "test.db"
        database.initialize_database()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        database.DATABASE_PATH = cls.original_database_path
        cls.temp_dir.cleanup()

    def setUp(self):
        self.teacher_id = self.client.post(
            "/teachers",
            json={
                "name": "Professor de teste",
                "description": "Professor para testes da API",
                "email": None,
            },
        ).json()["teacher_id"]
        self.student_id = self.client.post(
            "/students",
            json={
                "name": "Aluno de teste",
                "education_level": "Ensino Medio",
                "grade_or_period": "3o ano",
            },
        ).json()["student_id"]
        self.content_id = create_content(
            teacher_id=self.teacher_id,
            title="Funcoes",
            original_text="Conteudo sobre funcoes.",
            context=LearningContext(
                subject="Matematica",
                education_level="Ensino Medio",
                grade_or_period="3o ano",
                target_audience="Alunos",
                learning_goal="Compreender funcoes",
                assessment_focus=["dominio"],
            ),
        )

    def test_health_and_catalogs(self):
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")

        methods = self.client.get("/students/learning-methods")
        self.assertEqual(methods.status_code, 200)
        self.assertEqual(
            {item["id"] for item in methods.json()},
            {"flashcards", "mind_map", "infographic"},
        )

    def test_teacher_and_student_profiles(self):
        teachers = self.client.get("/teachers")
        students = self.client.get("/students")
        self.assertEqual(teachers.status_code, 200)
        self.assertEqual(students.status_code, 200)
        self.assertEqual(
            self.client.get(f"/teachers/{self.teacher_id}").json()["id"],
            self.teacher_id,
        )
        self.assertEqual(
            self.client.get(f"/students/{self.student_id}").json()["id"],
            self.student_id,
        )

    def test_teacher_upload_route_forwards_form_and_file(self):
        with patch(
            "app.api.teacher_routes.extract_text",
            return_value="Conteudo sobre funcoes.",
        ), patch(
            "app.api.teacher_routes.process_teacher_content",
            return_value={"content_id": "generated-content"},
        ) as process_content:
            response = self.client.post(
                f"/teachers/{self.teacher_id}/contents",
                data={
                    "title": "Funcoes",
                    "subject": "Matematica",
                    "education_level": "Ensino Medio",
                    "grade_or_period": "3o ano",
                    "target_audience": "Alunos",
                    "learning_goal": "Compreender funcoes",
                    "assessment_focus": "dominio",
                },
                files={
                    "file": (
                        "funcoes.pdf",
                        b"Conteudo sobre funcoes.",
                        "application/pdf",
                    )
                },
            )

        self.assertEqual(response.status_code, 200)
        process_content.assert_called_once()
        self.assertEqual(process_content.call_args.args[:3], (
            self.teacher_id,
            "Funcoes",
            "Conteudo sobre funcoes.",
        ))

    def test_student_can_be_assigned_and_list_content(self):
        assignment = self.client.post(
            f"/teachers/contents/{self.content_id}/students/{self.student_id}"
        )
        self.assertEqual(assignment.status_code, 200)

        contents = self.client.get(
            f"/students/{self.student_id}/contents"
        )
        self.assertEqual(contents.status_code, 200)
        self.assertEqual(contents.json()[0]["id"], self.content_id)

    def test_method_selection_and_material_generation(self):
        create_student_content(self.student_id, self.content_id)
        topic_id = create_topic(
            content_id=self.content_id,
            name="Funcoes",
            description="Relacoes entre conjuntos.",
            importance=5,
            difficulty=2,
            learning_objectives=["Identificar dominio"],
            concepts=["dominio"],
            practical_applications=["Interpretar relacoes"],
        )
        material = LearningMaterial(
            method="flashcards",
            title="Funcoes",
            summary="Resumo",
            flashcards=[
                Flashcard(
                    id=f"fc-{index}",
                    question=f"Pergunta {index}",
                    hint="Dica",
                    answer="Resposta",
                    difficulty=1,
                    concept="dominio",
                )
                for index in range(8)
            ],
        )

        selected = self.client.post(
            f"/students/{self.student_id}/contents/{self.content_id}/method",
            json={"method": "flashcards"},
        )
        self.assertEqual(selected.status_code, 200)

        with patch(
            "app.api.student_routes.generate_learning_material",
            return_value=material,
        ):
            generated = self.client.post(
                f"/students/{self.student_id}/contents/{self.content_id}/materials"
            )

        self.assertEqual(generated.status_code, 200)
        self.assertEqual(generated.json()["method"], "flashcards")
        self.assertEqual(generated.json()["material"]["title"], "Funcoes")
        self.assertIsNotNone(topic_id)

    def test_invalid_method_is_rejected(self):
        response = self.client.post(
            f"/students/{self.student_id}/contents/{self.content_id}/method",
            json={"method": "quiz"},
        )
        self.assertEqual(response.status_code, 400)

    def test_attempt_performance_adaptive_and_recommendation_history(self):
        create_student_content(self.student_id, self.content_id)
        create_topic(
            content_id=self.content_id,
            name="Funcoes",
            description="Relacoes entre conjuntos.",
            importance=5,
            difficulty=2,
            learning_objectives=["Identificar dominio"],
            concepts=["dominio"],
            practical_applications=["Interpretar relacoes"],
        )
        attempt = self.client.post(
            f"/students/{self.student_id}/materials/material-1/attempt",
            json={
                "item_id": "fc-1",
                "item_type": "flashcard",
                "concept": "dominio",
                "correct": False,
            },
        )
        self.assertEqual(attempt.status_code, 200)

        with patch(
            "app.services.adaptive_learning_service.generate_learning_material",
            return_value=LearningMaterial(
                method="flashcards",
                title="Funcoes",
                summary="Resumo",
                flashcards=[
                    Flashcard(
                        id=f"fc-{index}",
                        question=f"Pergunta {index}",
                        hint="Dica",
                        answer="Resposta",
                        difficulty=1,
                        concept="dominio",
                    )
                    for index in range(8)
                ],
            ),
        ):
            adaptive = self.client.post(
                f"/students/{self.student_id}/contents/{self.content_id}/adaptive"
            )
        self.assertEqual(adaptive.status_code, 200)
        self.assertIn("recommendation_id", adaptive.json())
        self.assertIn("status", adaptive.json())

        create_recommendation(
            self.student_id,
            self.content_id,
            "practicing",
            "generate_material",
            "flashcards",
            "Reforcar conceitos.",
        )
        history = self.client.get(
            f"/students/{self.student_id}/contents/{self.content_id}/recommendations"
        )
        self.assertEqual(history.status_code, 200)
        self.assertGreaterEqual(len(history.json()), 2)

    def test_adaptive_requires_topics(self):
        response = self.client.post(
            f"/students/{self.student_id}/contents/{self.content_id}/adaptive"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Conteúdo sem tópicos")


if __name__ == "__main__":
    unittest.main()
