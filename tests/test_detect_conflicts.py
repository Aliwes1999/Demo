"""
Test script to verify the detect_conflicts function with enhanced prompt.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ai_client import detect_conflicts

# Test requirements with known conflicts
test_requirements = [
    {
        "id": 1,
        "title": "Benutzer-Authentifizierung",
        "description": "Das System muss ein Benutzer-Login-System mit Benutzername und Passwort implementieren."
    },
    {
        "id": 2,
        "title": "Schnelle Anmeldung",
        "description": "Die Anmeldung muss in unter 500ms durchgeführt werden."
    },
    {
        "id": 3,
        "title": "Benutzer-Login",
        "description": "Der Benutzer soll sich mit seinen Anmeldedaten in das System einloggen können."
    },
    {
        "id": 4,
        "title": "System darf offline sein",
        "description": "Das System muss auch ohne Internetverbindung funktionieren."
    },
    {
        "id": 5,
        "title": "Cloud-Synchronisierung",
        "description": "Alle Daten müssen in Echtzeit mit der Cloud synchronisiert werden."
    },
    {
        "id": 6,
        "title": "Datensicherheit",
        "description": "Alle Passwörter müssen verschlüsselt gespeichert werden."
    },
    {
        "id": 7,
        "title": "Passwörter im Klartext",
        "description": "Passwörter sollen für bessere Performance im Klartext gespeichert werden."
    },
    {
        "id": 8,
        "title": "Benutzerfreundlichkeit",
        "description": "Das Interface soll intuitiv und einfach zu bedienen sein."
    },
    {
        "id": 9,
        "title": "Maximale Performance",
        "description": "Das System muss extrem schnell sein und mit minimaler Latenz reagieren."
    },
    {
        "id": 10,
        "title": "Kleine Speichergröße",
        "description": "Die Anwendung darf maximal 50MB Speicher benötigen."
    }
]

def test_detect_conflicts():
    """Test the detect_conflicts function."""
    print("=" * 80)
    print("TESTING detect_conflicts() with enhanced prompt")
    print("=" * 80)
    print(f"\nAnzahl der Anforderungen: {len(test_requirements)}\n")
    
    # Print input requirements
    print("EINGABE-ANFORDERUNGEN:")
    print("-" * 80)
    for req in test_requirements:
        print(f"ID {req['id']}: {req['title']}")
        print(f"  → {req['description'][:80]}...")
    
    print("\n" + "=" * 80)
    print("ANALYSE WIRD DURCHGEFÜHRT...")
    print("=" * 80 + "\n")
    
    # Call the function
    conflicts = detect_conflicts(test_requirements)
    
    # Print results
    if conflicts:
        print(f"ERKANNTE KONFLIKTE/PROBLEME: {len(conflicts)}\n")
        for i, conflict in enumerate(conflicts, 1):
            print(f"{i}. KONFLIKT/PROBLEM:")
            print(f"   Anforderung 1: ID {conflict.get('req_id_1', 'N/A')}")
            print(f"   Anforderung 2: ID {conflict.get('req_id_2', 'N/A')}")
            print(f"   Beschreibung: {conflict.get('description', 'N/A')}")
            print(f"   Severity: {conflict.get('severity', 'N/A')}")
            print()
    else:
        print("KEINE KONFLIKTE GEFUNDEN (leeres Array)")
    
    print("=" * 80)
    print("TEST ABGESCHLOSSEN")
    print("=" * 80)
    
    return conflicts

if __name__ == "__main__":
    try:
        results = test_detect_conflicts()
        print(f"\n✓ Test erfolgreich abgeschlossen!")
        print(f"✓ {len(results)} Konflikte/Probleme identifiziert")
    except Exception as e:
        print(f"\n✗ Fehler bei der Testausführung: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
