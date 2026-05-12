import os
import json
import re
import sys
from pathlib import Path
from openai import OpenAI

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import config

def generate_requirements(user_description: str | None, inputs: dict, columns: list = None, ai_model: str = None, num_requirements: int = None, num_requirements_mode: str | None = None, num_requirements_value: int | None = None, product_system: str = None, has_excel_context: bool = False, has_pdf_context: bool = False, improve_only: bool = False, extend_existing: bool = False, output_language: str | None = None) -> list[dict]:
    """
    Calls OpenAI API to generate requirements based on user description and inputs.

    Args:
        user_description (str | None): Optional user description of requirements.
        inputs (dict): Key-value pairs for additional context.
        columns (list): Optional list of column names for the project.
        ai_model (str): Optional AI model to use (overrides config default).
        num_requirements (int): Optional number of requirements to generate.
        product_system (str): Optional product system name for context.
        has_excel_context (bool): Whether Excel context is present in user_description.
        improve_only (bool): Whether to only improve existing requirements.
        extend_existing (bool): Whether to extend existing requirements.

    Returns:
        list[dict]: List of requirement dicts with dynamic columns based on project.
    
    Raises:
        ValueError: If OPENAI_API_KEY is not set.
        RuntimeError: If OpenAI API call fails or response is invalid.
    """
    # Get configuration
    api_key = config.OPENAI_API_KEY
    model = ai_model or config.OPENAI_MODEL or "gpt-4o-mini"
    system_prompt = config.get_system_prompt(
        columns,
    num_requirements,
    product_system,
    has_excel_context,
    has_pdf_context,
        improve_only,
        extend_existing,
        output_language,
        num_requirements_mode,
        num_requirements_value
    )

    # ... rest of the function stays the same

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set.")

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Build user message from user_description and inputs
    user_message_parts = []
    if output_language and output_language.strip():
        user_message_parts.append(f"Ausgabe-Sprache: {output_language.strip()}")
    
    if product_system and product_system.strip():
        user_message_parts.append(f"Produktsystem: {product_system.strip()}")
    
    if user_description and user_description.strip():
        user_message_parts.append(f"Beschreibung: {user_description.strip()}")
    
    if inputs:
        user_message_parts.append("\nZusätzliche Informationen:")
        for key, value in inputs.items():
            if key and value:
                user_message_parts.append(f"- {key}: {value}")
    
    if not user_message_parts:
        user_message = "Bitte generiere allgemeine Software-Anforderungen."
    else:
        user_message = "\n".join(user_message_parts)

    # Build developer message with dynamic JSON schema
    if columns and isinstance(columns, list):
        # Build JSON structure based on columns
        json_fields = []
        for col in columns:
            col_lower = col.lower()
            if col_lower in ['titel', 'title']:
                json_fields.append(f'      "{col}": "Kurzer, prägnanter Titel"')
            elif col_lower in ['beschreibung', 'description']:
                json_fields.append(f'      "{col}": "Detaillierte Beschreibung der Anforderung mit Akzeptanzkriterien"')
            elif col_lower in ['kategorie', 'category']:
                json_fields.append(
                    f'      "{col}": "Kategorie (z.B. nach der Hauptmerkmalliste nach Pahl/Beitz (hauptäschlich für Maschinen- und Anlagenbauprodukte): Geometrie, Kinematik, Kräfte, Energie, Stoff, Signal, Sicherheit, Ergonomie, Fertigung, Kontrolle, Montage, Transport, Gebrauch, Instandhaltung, Recycling, Kosten), Randbedingungen etc., vor allem für mechatronische Syteme weitere Kategorien möglich.)"'
                )
            elif col_lower in ['status']:
                json_fields.append(f'      "{col}": "Entwurf"')
            else:
                json_fields.append(f'      "{col}": "Passender Wert für {col}"')
        
        # Add is_quantifiable and is_functional fields
        json_fields.append('      "is_quantifiable": true oder false')
        json_fields.append('      "is_functional": true oder false')
        
        json_example = "{\n" + ",\n".join(json_fields) + "\n    }"
        
        developer_message = f"""Du musst ausschließlich mit gültigem JSON antworten.
Das JSON-Format muss exakt dieser Struktur folgen:
{{
  "requirements": [
    {json_example}
  ]
}}

Wichtig: 
- Fülle ALLE Spalten ({', '.join(columns)}) mit sinnvollen Werten.
- Setze "is_quantifiable" auf true, wenn die Anforderung quantitativ messbar ist (z.B. Performance-Werte, Zeitlimits, Durchsatz, Speicherverbrauch, etc.).
- Setze "is_quantifiable" auf false für qualitative Anforderungen (z.B. Benutzerfreundlichkeit, Design, etc.).
- Setze "is_functional" auf true, wenn die Anforderung explizit eine Funktion des zu entwickelnden Produkts oder Systems beschreibt.
- Setze "is_functional" auf false, wenn es sich um eine nicht-funktionale Anforderung handelt.
Erzeuge nicht nur 10 Anforderungen, sondern so viele wie möglich und sinnvoll, um den Kontext bestmöglich auszunutzen.
Antworte NUR mit diesem JSON, ohne zusätzlichen Text davor oder danach."""
    else:
        # Fallback to default structure
        developer_message = """Du musst ausschließlich mit gültigem JSON antworten.
Das JSON-Format muss exakt dieser Struktur folgen:
{
  "requirements": [
    {
      "title": "Kurzer, prägnanter Titel",
      "description": "Detaillierte Beschreibung mit Akzeptanzkriterien",
            "category": "Kategorie (z.B. nach der Hauptmerkmalliste nach Pahl/Beitz (hauptäschlich für Maschinen- und Anlagenbauprodukte): Geometrie, Kinematik, Kräfte, Energie, Stoff, Signal, Sicherheit, Ergonomie, Fertigung, Kontrolle, Montage, Transport, Gebrauch, Instandhaltung, Recycling, Kosten), Randbedingungen etc., vor allem für mechatronische Syteme weitere Kategorien möglich.)",
            "status": "Entwurf",
            "is_quantifiable": true oder false,
            "is_functional": true oder false
    }
  ]
}

Wichtig: 
- Setze "is_quantifiable" auf true, wenn die Anforderung quantitativ messbar ist (z.B. Performance-Werte, Zeitlimits, Durchsatz, etc.).
- Setze "is_quantifiable" auf false für qualitative Anforderungen (z.B. Benutzerfreundlichkeit, Design, etc.).
- Setze "is_functional" auf true, wenn die Anforderung explizit eine Funktion des zu entwickelnden Produkts oder Systems beschreibt.
- Setze "is_functional" auf false, wenn es sich um eine nicht-funktionale Anforderung handelt.
Erzeuge nicht nur 10 Anforderungen, sondern so viele wie möglich und sinnvoll, um den Kontext bestmöglich auszunutzen.

Antworte NUR mit diesem JSON, ohne zusätzlichen Text davor oder danach."""

    try:
        # Call OpenAI Chat Completions API
        max_output_tokens = 8000
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "developer", "content": developer_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            max_tokens=max_output_tokens
        )

        # Extract response content
        response_text = response.choices[0].message.content.strip()

        # Parse JSON response
        requirements = _parse_json_response(
            response_text,
            columns,
            num_requirements,
            num_requirements_mode,
            num_requirements_value
        )
        
        return requirements

    except Exception as e:
        raise RuntimeError(f"OpenAI request failed: {str(e)}")


def _parse_json_response(response_text: str, columns: list = None, num_requirements: int = None, num_requirements_mode: str | None = None, num_requirements_value: int | None = None) -> list[dict]:
    """
    Robustly parse JSON response from OpenAI, with fallback to regex extraction.

    Args:
        response_text (str): Raw response text from OpenAI.
        columns (list): Optional list of column names for validation.
        num_requirements (int): Optional number of requirements to return.

    Returns:
        list[dict]: List of validated and normalized requirement dicts.
    
    Raises:
        RuntimeError: If JSON cannot be parsed or is invalid.
    """
    # Try direct JSON parsing first
    try:
        data = json.loads(response_text)
        if isinstance(data, dict) and "requirements" in data:
            return _validate_and_normalize_requirements(
                data["requirements"],
                columns,
                num_requirements,
                num_requirements_mode,
                num_requirements_value
            )
    except json.JSONDecodeError:
        pass

    # Fallback: Extract JSON block using regex
    # Look for JSON object that contains "requirements"
    json_pattern = r'\{[^{}]*"requirements"[^{}]*\[[^\]]*\][^{}]*\}'
    # More robust pattern that handles nested structures
    json_pattern = r'\{(?:[^{}]|\{[^{}]*\})*"requirements"(?:[^{}]|\{[^{}]*\})*\[(?:[^\[\]]|\[[^\[\]]*\])*\](?:[^{}]|\{[^{}]*\})*\}'
    
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    for match in matches:
        try:
            data = json.loads(match)
            if isinstance(data, dict) and "requirements" in data:
                return _validate_and_normalize_requirements(
                    data["requirements"],
                    columns,
                    num_requirements,
                    num_requirements_mode,
                    num_requirements_value
                )
        except json.JSONDecodeError:
            continue

    # If still no valid JSON found, try to extract just the array
    array_pattern = r'\[\s*\{[^\]]+\}\s*\]'
    array_matches = re.findall(array_pattern, response_text, re.DOTALL)
    
    for match in array_matches:
        try:
            data = json.loads(match)
            if isinstance(data, list):
                return _validate_and_normalize_requirements(
                    data,
                    columns,
                    num_requirements,
                    num_requirements_mode,
                    num_requirements_value
                )
        except json.JSONDecodeError:
            continue

    raise RuntimeError("Invalid JSON response from model: Could not parse requirements structure.")


def _validate_and_normalize_requirements(requirements: list, columns: list = None, num_requirements: int = None, num_requirements_mode: str | None = None, num_requirements_value: int | None = None) -> list[dict]:
    """
    Validate and normalize requirements list with support for dynamic columns.

    Args:
        requirements (list): Raw requirements list from parsed JSON.
        columns (list): Optional list of column names to validate against.
        num_requirements (int): Optional number of requirements to return.

    Returns:
        list[dict]: Validated and normalized requirements.
    
    Raises:
        RuntimeError: If requirements structure is invalid.
    """
    if not isinstance(requirements, list):
        raise RuntimeError("Requirements must be a list.")

    normalized = []
    
    for req in requirements:
        if not isinstance(req, dict):
            continue
        
        # If columns are provided, use them for validation
        if columns and isinstance(columns, list):
            normalized_req = {}
            has_required_data = False
            
            for col in columns:
                value = str(req.get(col, "")).strip()
                normalized_req[col] = value
                
                # Check if we have at least some meaningful data
                if value:
                    has_required_data = True
            
            # Only add if we have at least some data
            if has_required_data:
                normalized.append(normalized_req)
        else:
            # Fallback to default validation (backward compatibility)
            title = req.get("title", "").strip()
            description = req.get("description", "").strip()
            
            if not title or not description:
                continue  # Skip invalid requirements
            
            # Set defaults for optional fields
            category = req.get("category", "").strip()
            status = req.get("status", "Entwurf").strip()
            
            # Ensure status is "Entwurf" als Standard
            if status != "Entwurf":
                status = "Entwurf"
            
            normalized.append({
                "title": title,
                "description": description,
                "category": category,
                "status": status
            })
    
    if not normalized:
        raise RuntimeError("No valid requirements found in response.")
    
    # Limit results based on mode/value with hard cap
    max_cap = 1000
    if num_requirements_mode == "max" and num_requirements_value and num_requirements_value > 0:
        return normalized[:min(num_requirements_value, max_cap)]
    if num_requirements_mode == "exact" and num_requirements_value and num_requirements_value > 0:
        return normalized[:min(num_requirements_value, max_cap)]
    if num_requirements and num_requirements > 0:
        return normalized[:min(num_requirements, max_cap)]
    if num_requirements_mode == "auto" or not num_requirements_mode:
        return normalized
    if num_requirements_mode == "min":
        return normalized[:max_cap]
    return normalized


def detect_conflicts(requirements_list: list[dict]) -> list[dict]:
    """
    Analyzes a complete requirements set for quality assurance including logical contradictions,
    redundancy, completeness, consistency, priorities, structure, modifiability, clarity,
    testability, feasibility, traceability, and stakeholder coverage using AI.

    Args:
        requirements_list (list[dict]): List of dicts representing requirements (title, description).

    Returns:
        list[dict]: List of detected conflicts, issues, and problems.
    """
    # Get configuration
    api_key = config.OPENAI_API_KEY
    model = config.OPENAI_MODEL or "gpt-4o-mini"
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set.")
    
    if not requirements_list or len(requirements_list) < 2:
        return []

    client = OpenAI(api_key=api_key)

    # Define system prompt once before the loop (optimization)
    system_prompt = """
    Du bist ein Experte für Requirements Engineering und willst deine gesamte Anforderungsliste auf Qualität und Logik prüfen.
    Deine Aufgabe ist es, eine Liste von Anforderungen systematisch auf folgende Aspekte zu analysieren:

    ANALYSE-KRITERIEN:
    1. Konflikte und Widersprüche: Zwei Anforderungen, die nicht gleichzeitig erfüllt werden können
    2. Redundanz: Anforderungen mit gleichem Inhalt, die unterschiedlich ausgedrückt sind
    3. Vollständigkeit: Abdeckung aller funktionalen und nicht-funktionalen Anforderungen für das System und seinen Umfang
    4. Konsistenz: Kohärenz und Widerspruchsfreiheit der gesamten Anforderungsmenge
    5. Prioritäten: Korrekte Kennzeichnung von Must/Should/Can-Anforderungen
    6. Strukturierung: Logische Organisation und Gruppierung der Anforderungen
    7. Modifizierbarkeit: Individuelle Formulierung, leichte Anpassbarkeit, keine gemischten oder zu langen Anforderungen
    8. Klarheit und Verständlichkeit: Eindeutigkeit der Formulierungen
    9. Testbarkeit und Verifizierbarkeit: Anforderungen müssen überprüfbar sein (Erstellung von Testfällen möglich)
    10. Machbarkeit: Realistische und implementierbare Anforderungen
    11. Rückverfolgbarkeit: Verfolgbarkeit von Anforderungen durch das System
    12. Stakeholder-Abdeckung: Berücksichtigung aller Stakeholder (Nutzer, Betreiber, Hersteller, rechtliche Anforderungen)

    Analysiere die Anforderungen sorgfältig und erkenne auch potenzielle Gefahren, Probleme und zukünftige Schwierigkeiten, selbst wenn keine direkten Widersprüche vorhanden sind.

    WICHTIG: Setze req_id_1 und req_id_2 IMMER als die exakten Zahlen aus der Eingabe (z.B. ID 1, ID 2). Verwende NIEMALS 'undefined', Platzhalter oder andere IDs. Beschreibe die Problematik mit den gleichen IDs, die du in req_id_1 und req_id_2 setzt.

    Antworte ausschließlich mit gültigem JSON in folgender Struktur:
    {
        "conflicts": [
            {
                "req_id_1": 1,
                "req_id_2": 2,
                "description": "Erklärung des Konflikts/der Problematik mit ID 1 und ID 2",
                "severity": "Hoch" (oder "Mittel", "Niedrig")
            }
        ]
    }

    Wenn keine Konflikte oder Probleme gefunden werden, antworte mit: {"conflicts": []}
    """

    # Prepare requirements text - shorten descriptions to avoid AI overload
    req_text = ""
    for idx, req in enumerate(requirements_list):
        req_text += f"ID {req['id']}: {req['title']}\nDescription: {req['description'][:150]}\n\n"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Hier sind die Anforderungen:\n\n{req_text}"}
            ],
            temperature=0.1,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )

        response_text = response.choices[0].message.content.strip()
        data = json.loads(response_text)
        return data.get("conflicts", [])

    except Exception as e:
        print(f"Error checking conflicts: {e}")
        return []


def generate_test_cases(title: str, description: str) -> str:
    """
    Generates Gherkin test cases and acceptance criteria for a single requirement.

    Args:
        title (str): Requirement title.
        description (str): Requirement description.

    Returns:
        str: Generated test cases text.
    """
    api_key = config.OPENAI_API_KEY
    model = config.OPENAI_MODEL or "gpt-4o-mini"
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)

    system_prompt = """
    Du bist ein QA-Test-Ingenieur.
    Deine Aufgabe ist es, für eine gegebene Software-Anforderung detaillierte Testfälle zu erstellen.
    
    Format:
    1. Akzeptanzkriterien (Liste)
    2. Gherkin Szenarien (Given-When-Then)
    
    Antworte direkt mit dem Text (Markdown), ohne JSON-Formatierung.
    """
    
    user_message = f"Anforderung: {title}\nBeschreibung: {description}\n\nBitte erstelle Testfälle."

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler bei der Generierung: {str(e)}"

def analyze_requirement(title: str, description: str, status: str) -> dict:
    """
    Analyze a single requirement and return a structured assessment.

    Args:
        title (str): Requirement title.
        description (str): Requirement description.
        status (str): Current requirement status.

    Returns:
        dict: Analysis result as structured JSON-compatible dict.
    """
    api_key = config.OPENAI_API_KEY
    model = config.OPENAI_MODEL or "gpt-4o-mini"

    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)

    system_prompt = """
    Du bist ein erfahrener Requirements Engineer mit Kenntnissen in Best Practices des Model-Based Systems Engineering.
    Deine Aufgabe ist es, eine einzelne Anforderung zu analysieren, zu prüfen und eine unterstützende Bewertung zu liefern. Die Bewertung dient nur als Orientierung für weitere iterative Verbesserung der AnforderungsFORMULIERUNG, um sie optimal wie möglich zu gestalten (Qualitätskriterien: nachweisbar, korrekt, eindeutig, notwendig, identifizierbar/verfolgbar/nachvollziehbar, verständlich, Konsistenz, Singularität, Realisierbarkeit, Notwendigkeit).

    Regeln:
    - Verändere nicht den Inhalt der Anforderung.
    - Erstelle keine neuen Anforderungen.
    - Bewerte nur die Anforderung.
    - Orientiere dich methodisch an SysML v2 (z.B. Constraints in Anforderungen: messbar, quantifizierbar, parametrisierbar).

    Antworte ausschließlich mit gültigem JSON in der folgenden Struktur:
    {
      "functional_assessment": {
        "Kategorisierung": "Kurz begründen, warum es genau zu dieser Kategorie gehören sollte und es so optimal wäre",
        "completeness": "kurze Einschätzung zur Vollständigkeit innerhalb der formulierten einzelnen Anforderung",
        "clarity": "kurze Einschätzung zur Verständlichkeit/Klarheit/Eindeutigkeit (klar, einfach formuliert; keine unnötig komplizierten Sätze; keine langen, vermischten Sätze)",
        "correctness": "kurze Einschätzung zur fachlichen Korrektheit und auch Notwendigkeit (jede Anforderung hat klaren Zweck, keine \"nice-to-have\"-Formulierungen ohne Begründung)",
        "feasibility": "kurze Einschätzung zur Realisierbarkeit (technisch, wirtschaftlich)/Verfolgbarkeit/Nachvollziehbarkeit",
        "verifiability": "kurze Einschätzung zur Messbarkeit / Überprüfbarkeit (Verifizierbarkeit)",
        "summary": "kurze, nachvollziehbare Gesamteinschätzung und Bewertung nach dem SMART-Prinzip: Spezifisch (klar und eindeutig formuliert); Messbar (überprüfbar durch Zahlen / Grenzwerte – nur falls messbare Anforderung); Akzeptiert/Achievable (Erreichbar – keine unrealistischen Forderungen); Realistisch (sinnvoll im Kontext (z.B. Kosten, Technik, Einsatz), passt zum System und Zweck); Terminiert (zeitlicher Bezug (falls relevant), z.B. Reaktionszeit, Lebensdauer etc.)"
      },
      "quantifiable_assessment": {
        "has_metric": true|false,
        "metric": "erkannte, eindeutig formulierte Messgröße/n oder leer",
        "constraint": "SysML-Constraint-Form (z.B. \"responseTime <= 3 s\") oder leer",
        "is_quantifiable": true|false
      }
    }
    """

    user_message = (
        "Bitte analysiere die folgende Anforderung.\n\n"
        f"Titel: {title}\n"
        f"Beschreibung: {description}\n"
        f"Status: {status}\n"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            max_tokens=900,
            response_format={"type": "json_object"}
        )
        response_text = response.choices[0].message.content.strip()
        return json.loads(response_text)
    except Exception as e:
        return {"error": f"Fehler bei der Analyse: {str(e)}"}


def improve_requirement_from_analysis(analysis: dict, title: str, description: str, status: str) -> dict:
    """
    Generate improvement suggestion based on analysis results.

    Args:
        analysis (dict): Analysis result from analyze_requirement().
        title (str): Current requirement title.
        description (str): Current requirement description.
        status (str): Current requirement status.

    Returns:
        dict: Improvement suggestion with improved_title, improved_description, and rationale.
    """
    api_key = config.OPENAI_API_KEY
    model = config.OPENAI_MODEL or "gpt-4o-mini"

    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)

    # Extract key findings from analysis
    weakness_points = []
    functional_assessment = analysis.get("functional_assessment", {})
    
    if functional_assessment:
        if "clarity" in functional_assessment:
            clarity = functional_assessment["clarity"].lower()
            if "schwach" in clarity or "unklar" in clarity or "verbesserung" in clarity:
                weakness_points.append(f"Klarheit: {functional_assessment['clarity']}")
        
        if "verifiability" in functional_assessment:
            verif = functional_assessment["verifiability"].lower()
            if "schwach" in verif or "nicht messbar" in verif or "verbesserung" in verif:
                weakness_points.append(f"Messbarkeit: {functional_assessment['verifiability']}")
        
        if "completeness" in functional_assessment:
            complete = functional_assessment["completeness"].lower()
            if "unvollständig" in complete or "fehlendes" in complete:
                weakness_points.append(f"Vollständigkeit: {functional_assessment['completeness']}")

    system_prompt = """
    Du bist ein erfahrener Requirements Engineer mit Kenntnissen in Best Practices des Model-Based Systems Engineering.
    Deine Aufgabe ist es, basierend auf vorliegenden Schwachstellen einer Anforderung, konkrete Verbesserungsvorschläge zu machen.

    Regeln:
    - Verbessere nur die identifizierten Schwachstellen, keine unnötigen Änderungen.
    - Behalte den Sinn und die Absicht der ursprünglichen Anforderung bei.
    - Mache den Text klarer, messbarer und eindeutiger.
    - Orientiere dich methodisch an SysML v2 Best Practices.
    - Nutze konkrete, messbare Kriterien where applicable.

    Antworte ausschließlich mit gültigem JSON in der folgenden Struktur:
    {
      "improved_title": "Verbesserte Titelformulierung",
      "improved_description": "Verbesserte Beschreibung mit klaren Anforderungen und Messbarkeit where applicable",
      "improvement_rationale": "Kurze Erklärung, welche Schwachstellen behoben wurden",
      "improvements": ["Punkt 1", "Punkt 2", ...]
    }
    """

    weakness_text = "\n".join(weakness_points) if weakness_points else "Allgemeine Verbesserung der Anforderungsqualität"

    user_message = (
        "Basierend auf der Analyse einer Anforderung wurden folgende Schwachstellen identifiziert:\n\n"
        f"{weakness_text}\n\n"
        "ORIGINALE ANFORDERUNG:\n"
        f"Titel: {title}\n"
        f"Beschreibung: {description}\n"
        f"Status: {status}\n\n"
        "Bitte erstelle einen VERBESSERTEN Vorschlag für diese Anforderung, der die identifizierten Schwachstellen behebt."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        response_text = response.choices[0].message.content.strip()
        return json.loads(response_text)
    except Exception as e:
        return {"error": f"Fehler beim Erstellen des Verbesserungsvorschlags: {str(e)}"}


def generate_specification_document(requirements_list: list[dict], doc_type: str) -> str:
    """
    Generates a specification document (Lastenheft or Pflichtenheft) from a list of requirements.

    Args:
        requirements_list (list[dict]): List of requirement dicts with 'title' and 'description'.
        doc_type (str): Type of document, either 'lastenheft' or 'pflichtenheft'.

    Returns:
        str: Generated document in Markdown format.
    
    Raises:
        ValueError: If doc_type is invalid or OPENAI_API_KEY is not set.
        RuntimeError: If OpenAI API call fails.
    """
    # Get configuration
    api_key = config.OPENAI_API_KEY
    model = config.OPENAI_MODEL or "gpt-4o-mini"
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set.")
    
    if doc_type not in ['lastenheft', 'pflichtenheft']:
        raise ValueError("doc_type must be 'lastenheft' or 'pflichtenheft'.")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Set system prompt based on doc_type
    if doc_type == 'lastenheft':
        system_prompt = """
Du bist ein hochqualifizierter Senior Requirements Engineer und Systemanalytiker.
Deine Aufgabe ist es, aus einer übergebenen Liste von Roh-Anforderungen ein professionelles, detailliertes Lastenheft (Product Requirements Document) zu erstellen.

ZIEL DES DOKUMENTS:
Das Lastenheft beschreibt die Gesamtheit der Forderungen des Auftraggebers an die Lieferungen und Leistungen des Auftragnehmers. Es fokussiert sich ausschließlich auf das WAS und WOFÜR (Zweck, Ziele, Systemgrenzen), nicht auf die technische Umsetzung.

STRUKTURVORGABE (Halte dich strikt an dieses Markdown-Template):
# Lastenheft

## 1. Einführung und Zielsetzung
[Fasse den Hauptzweck des Systems basierend auf den Anforderungen in 2-3 Absätzen zusammen. Was ist der geschäftliche Wert?]

## 2. Systemgrenzen und Kontext
[Definiere, was zum System gehört und was explizit nicht dazu gehört, abgeleitet aus den Daten.]

## 3. Funktionale Anforderungen
[Gruppiere hier alle funktionalen Anforderungen logisch. Nutze Tabellen oder klare Listen. Referenziere IMMER die originale ID der Anforderung (z.B. REQ-1).]

## 4. Nicht-funktionale Anforderungen & Rahmenbedingungen
[Führe hier Performance, Sicherheit, Ergonomie, und andere Qualitätsmerkmale auf. Beachte besonders Anforderungen, die als 'is_quantifiable: true' markiert sind.]

## 5. Abnahmekriterien
[Fasse zusammen, woran der Erfolg des Projekts gemessen wird.]

REGELN UND EINSCHRÄNKUNGEN:
- ERFINDE KEINE neuen Anforderungen, Funktionen oder Stakeholder, die nicht im bereitgestellten Text stehen.
- Wenn Informationen für ein Kapitel fehlen, schreibe: "Basierend auf den aktuellen Anforderungen liegen hierzu keine Informationen vor."
- Formuliere präzise, objektiv und im professionellen Business-Kontext.
- Gib AUSSCHLIESSLICH das fertige Markdown-Dokument zurück. Keine Einleitung, keine Erklärungen davor oder danach.
"""
    elif doc_type == 'pflichtenheft':
        system_prompt = """
Du bist ein erfahrener Systemarchitekt und Model-Based Systems Engineering (MBSE) Experte.
Deine Aufgabe ist es, aus einer übergebenen Liste von Systemanforderungen ein detailliertes Pflichtenheft (System Requirements Specification) zu erstellen.

ZIEL DES DOKUMENTS:
Das Pflichtenheft beschreibt in konkreter Form, WIE und WOMIT die im Lastenheft formulierten Anforderungen technisch umgesetzt werden. Es dient als Grundlage für die Entwickler.

STRUKTURVORGABE (Halte dich strikt an dieses Markdown-Template):
# Pflichtenheft

## 1. Systemarchitektur und Lösungsansatz
[Beschreibe das grundlegende technische Konzept und die Systemarchitektur, die sich aus den Anforderungen ableiten lässt.]

## 2. Technische Umsetzung der Funktionen
[Gliedere die funktionalen Anforderungen in technische Module oder Komponenten. Wie werden diese software- oder hardwaretechnisch realisiert? Beziehe dich auf die Original-IDs.]

## 3. Datenmodell und Schnittstellen
[Welche Daten müssen verarbeitet werden? Welche internen oder externen Schnittstellen (APIs, Signale, Stoffflüsse) lassen sich aus den Anforderungen ableiten?]

## 4. Systemanforderungen und Constraints (SysML v2 Kontext)
[Analysiere die quantifizierbaren Anforderungen und formuliere sie als messbare technische Constraints (z.B. Antwortzeit <= 3s, Speicherlimit). Nutze MBSE-Prinzipien.]

## 5. Entwicklungs- und Betriebsumgebung
[Fasse zusammen, welche Rahmenbedingungen für die Entwicklung und den späteren Betrieb gelten.]

REGELN UND EINSCHRÄNKUNGEN:
- Erfinde keine absurden technischen Details, sondern leite realistische, branchenübliche Architekturansätze aus den Anforderungen ab.
- Behalte den Bezug zu den originalen Anforderungs-IDs stets bei, um Traceability (Rückverfolgbarkeit) zu gewährleisten.
- Wenn der übergebene Text keine Rückschlüsse auf ein Kapitel zulässt, notiere: "Technischer Ansatz noch zu definieren."
- Gib AUSSCHLIESSLICH das fertige Markdown-Dokument zurück. Keine Erklärungen davor oder danach.
"""
    
    # Build user message from requirements_list
    req_text = ""
    for req in requirements_list:
        title = req.get('title', 'Unbekannter Titel')
        description = req.get('description', 'Keine Beschreibung')
        req_text += f"Titel: {title}\nBeschreibung: {description}\n\n"
    
    user_message = f"Hier sind die Anforderungen:\n\n{req_text}"
    
    try:
        # Call OpenAI Chat Completions API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            max_tokens=4000
        )
        
        # Extract and return response content
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        raise RuntimeError(f"OpenAI request failed: {str(e)}")
