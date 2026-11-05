import os
import random
import re
import uuid

from locust import HttpUser, between, task
from locust.exception import StopUser

class StudentUser(HttpUser):
    """Simulates a student generating an AI requirement list."""

    wait_time = between(2, 6)

    def on_start(self):
        """Log in and create exactly one project for this virtual user."""
        self.email = os.getenv("LOCUST_EMAIL", "parbeit131@gmail.com")
        self.password = os.getenv("LOCUST_PASSWORD", "12345")
        self.ai_model = os.getenv(
            "LOCUST_AI_MODEL",
            "kiconnect:qwen-qwen3-8-27b",
        )

        with self.client.post(
            "/auth/login",
            data={"email": self.email, "password": self.password},
            name="POST /auth/login",
            catch_response=True,
        ) as response:
            if response.status_code not in (200, 302):
                response.failure(f"Login fehlgeschlagen: HTTP {response.status_code}")
                raise StopUser()

            if "/auth/login" in response.url:
                response.failure("Login fehlgeschlagen: Loginseite wurde erneut angezeigt.")
                raise StopUser()

        self.project_id = self._create_test_project()

    def _create_test_project(self):
        project_name = f"Locust-Test-{uuid.uuid4().hex[:12]}"

        with self.client.post(
            "/create",
            data={"project_name": project_name},
            name="POST /create (test project)",
            catch_response=True,
        ) as response:
            if response.status_code not in (200, 302):
                response.failure(f"Projekt konnte nicht erstellt werden: HTTP {response.status_code}")
                raise StopUser()

            project_match = re.search(
                rf'data-name="{re.escape(project_name.lower())}".*?'
                rf"window\.location='/project/(\d+)'",
                response.text,
                re.DOTALL,
            )
            if not project_match:
                response.failure(
                    "Projekt wurde nicht im Dashboard gefunden. "
                    "Prüfe LOCUST_EMAIL und LOCUST_PASSWORD."
                )
                raise StopUser()

            return project_match.group(1)

    @task
    def generate_requirement_list(self):
        """Generate exactly one requirement list in this user's project."""
        topics = [
            "Benutzerverwaltung",
            "Zahlungsabwicklung",
            "Sensordatenverarbeitung",
            "Berichtserstellung",
            "Rollen- und Rechteverwaltung",
        ]
        topic = random.choice(topics)

        form_data = {
            "product_system": "Webanwendung für Anforderungsmanagement",
            "user_description": (
                f"Generiere testbare Anforderungen für den Bereich {topic}."
            ),
            "num_requirements_mode": "exact",
            "num_requirements_value": "3",
            "ai_model": self.ai_model,
            "output_language": "Deutsch",
            "improve_only": "false",
            "extend_existing": "false",
        }

        with self.client.post(
            f"/agent/generate/{self.project_id}",
            data=form_data,
            name="POST /agent/generate/:project_id",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Generierung fehlgeschlagen: HTTP {response.status_code}")
                return

            try:
                result = response.json()
            except ValueError:
                response.failure("Generierung lieferte kein JSON.")
                return

            if not result.get("ok"):
                response.failure(result.get("error", "Backend meldet einen Fehler."))
            elif not isinstance(result.get("count"), int):
                response.failure("Antwort enthält keine gültige Anzahl generierter Anforderungen.")

        raise StopUser()