from locust import HttpUser, task, between

class StudentUser(HttpUser):
    # Simuliert 2 bis 6 Sekunden Lese-/Tippzeit zwischen den Klicks
    wait_time = between(2, 6)

    def on_start(self):
        """1. Login: Wird einmalig ausgeführt, wenn der Student die Seite betritt"""
        # WICHTIG: Trage hier die Daten eines Benutzers ein, der Zugriff auf Projekt ID 1 hat!
        self.client.post("/auth/login", data={
            "email": "dein_test_user@email.com",  # <-- ANPASSEN!
            "password": "dein_passwort"           # <-- ANPASSEN!
        })

    @task(3)
    def view_dashboard(self):
        """2. Startseite: Die Liste der Projekte aufrufen"""
        self.client.get("/")

    @task(3)
    def view_project(self):
        """3. Projektübersicht: Ein spezifisches Projekt aufrufen"""
        # Wir nehmen an, dass es ein Projekt mit der ID 1 gibt
        self.client.get("/project/1")

    @task(1)
    def ask_ai_chat(self):
        """4. KI Chat: Simuliert das Stellen einer Frage an den Projekt-Chatbot"""
        # Deine Route erwartet ein JSON mit dem Key 'question'
        self.client.post("/project/1/chat", json={
            "question": "Kannst du mir eine neue Anforderung für das Login-System generieren?"
        })

    @task(1)
    def create_manual_requirement(self):
        """5. Manuelle Anforderung: Simuliert das Speichern einer neuen Anforderung"""
        # Deine Route erwartet Formular-Daten (x-www-form-urlencoded)
        self.client.post("/project/1/manual_requirement", data={
            "title": "Automatische Lasttest-Anforderung",
            "description": "Diese Anforderung wurde durch Locust generiert.",
            "category": "Funktional",
            "status": "Entwurf",
            "funktional": "on"
        })