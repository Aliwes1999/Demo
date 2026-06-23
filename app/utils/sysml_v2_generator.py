import pandas as pd
from datetime import datetime

# ==========================================
# 1.Diese bearbeitete Version vom Sysml Generator ist für das Lesen von den Requirements direkt aus der webansicht, statt aus dem Download Ordner 
# ==========================================

def sanitize_package_name(category):
    category_mapping = {
        "Sicherheit": "SafetyRequirements",
        "Leistung": "PerformanceRequirements",
        "Funktional": "FunctionalRequirements",
        "Nicht-Funktional": "NonFunctionalRequirements",
        "Usability": "UsabilityRequirements",
        "Zuverlässigkeit": "ReliabilityRequirements",
        "Wartbarkeit": "MaintainabilityRequirements",
        "Kompatibilität": "CompatibilityRequirements",
    }
    if category in category_mapping:
        return category_mapping[category]
    sanitized = str(category).replace(" ", "").replace("-", "").replace("_", "")
    return f"{sanitized}Requirements"


def sanitize_requirement_id(req_id):
    return str(req_id).replace("-", "_").replace(" ", "_").replace(".", "_")


def escape_string(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    return text

# ==========================================
# 2. ANGEPASSTE GENERATOR-FUNKTION
# ==========================================
# Anstatt in eine Datei zu schreiben, gibt diese Funktion 
# nun den fertigen Code als String zurück.

def generate_sysmlv2_code(df):
    """
    Generiert SysML v2 Code aus dem DataFrame und gibt ihn als String zurück.
    """
    categories = df["Kategorie"].unique()
    sysml_code = []
    
    sysml_code.append("// SysML v2 Requirements Model")
    sysml_code.append("// Automatisch generiert am " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sysml_code.append("")
    sysml_code.append("// ========================================")
    sysml_code.append("// Metadaten-Definition")
    sysml_code.append("// ========================================")
    sysml_code.append("")
    sysml_code.append("metadata def RequirementMetadata {")
    sysml_code.append("    attribute 'verantwortlicher';")
    sysml_code.append("    attribute 'revision';")
    sysml_code.append("    attribute 'version';")
    sysml_code.append("    attribute 'status';")
    sysml_code.append("}")
    sysml_code.append("")
    sysml_code.append("package 'Requirements' {")
    sysml_code.append("view 'Requirements' : DS_Views::SymbolicViews::gv {")
    sysml_code.append("// ========================================")
    sysml_code.append("// Requirements Definitionen")
    sysml_code.append("// ========================================")
    sysml_code.append("")

    # --- Haupt-Package generieren ---
    for index, row in df.iterrows():
        req_id = sanitize_requirement_id(row["ID"])
        req_name = escape_string(row["Anforderung"])
        req_description = escape_string(row["Beschreibung"])
        verantwortlicher = escape_string(row["Verantwortlicher"]).split("@", 1)[0]
        revision = escape_string(row["Revision"])
        if revision.lower() == "entwurf":
            revision = ""
        version = escape_string(row["Version"])
        status = escape_string(row["Status"])
        
        sysml_code.append(f"requirement <REQ{req_id}> '{req_name}' {{")
        sysml_code.append("    doc /*")
        sysml_code.append(f"    {req_description}")
        sysml_code.append("    */")
        sysml_code.append("    ")
        sysml_code.append("    metadata RequirementMetadata {")
        sysml_code.append(f"        verantwortlicher = \"{verantwortlicher}\";")
        sysml_code.append(f"        revision = \"{revision}\";")
        sysml_code.append(f"        version = \"{version}\";")
        sysml_code.append(f"        status = \"{status}\";")
        sysml_code.append("    }")
        sysml_code.append("}")
        sysml_code.append("")

    sysml_code.append("}")
    sysml_code.append("}")

    # --- Kategorie-Packages generieren ---
    sysml_code.append("")
    sysml_code.append("// ========================================")
    sysml_code.append("// Requirement-Kategorien als Packages")
    sysml_code.append("// ========================================")
    sysml_code.append("")

    for category in categories:
        if category == "-" or pd.isna(category):
            continue
            
        package_name = sanitize_package_name(category)
        sysml_code.append(f"package '{package_name}' {{")
        sysml_code.append(f"    view '{package_name}' : DS_Views::SymbolicViews::gv {{")
        sysml_code.append("")

        for index, row in df.iterrows():
            category_ = row["Kategorie"]
            if sanitize_package_name(category_) == package_name:
                req_id = sanitize_requirement_id(row["ID"])
                req_name = escape_string(row["Anforderung"])
                req_description = escape_string(row["Beschreibung"])
                verantwortlicher = escape_string(row["Verantwortlicher"]).split("@", 1)[0]
                revision = escape_string(row["Revision"])
                if revision.lower() == "entwurf":
                    revision = ""
                version = escape_string(row["Version"])
                status = escape_string(row["Status"])

                sysml_code.append(f"requirement <REQ{req_id}> '{req_name}' {{")
                sysml_code.append("    doc /*")
                sysml_code.append(f"    {req_description}")
                sysml_code.append("    */")
                sysml_code.append("    ")
                sysml_code.append("    metadata RequirementMetadata {")
                sysml_code.append(f"        verantwortlicher = \"{verantwortlicher}\";")
                sysml_code.append(f"        revision = \"{revision}\";")
                sysml_code.append(f"        version = \"{version}\";")
                sysml_code.append(f"        status = \"{status}\";")
                sysml_code.append("    }")
                sysml_code.append("}")
                sysml_code.append("")
                
        sysml_code.append("}")
        sysml_code.append("}")

    # Gib die Liste als zusammenhängenden String zurück
    return "\n".join(sysml_code)