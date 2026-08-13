import json
import re
from pathlib import Path


# Location of healthcare dataset
DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "jeevansetu_diseases_v2.json"
)


def load_diseases():
    """Load disease information from the JSON file."""
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


diseases = load_diseases()


def _normalize_text(text: str) -> str:
    """Normalize text for simple symptom matching."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _tokens(text: str) -> set[str]:
    """Return useful word tokens."""
    stop_words = {
        "i",
        "have",
        "has",
        "had",
        "a",
        "an",
        "the",
        "and",
        "or",
        "am",
        "is",
        "are",
        "my",
        "me",
        "with",
        "of",
        "to",
        "in",
        "for",
        "what",
        "why",
        "how",
        "do",
        "does",
        "can",
        "you",
        "tell",
        "about",
    }

    return {
        word
        for word in _normalize_text(text).split()
        if word not in stop_words and len(word) > 2
    }


def _symptom_matches(query: str, symptom: str) -> int:
    """Calculate how many query words overlap with a symptom."""
    query_words = _tokens(query)
    symptom_words = _tokens(symptom)

    return len(query_words & symptom_words)


def find_diseases(query: str, limit: int = 3):
    """
    Retrieve diseases relevant to the user's question.

    Matches against:
    - disease name
    - description
    - common symptoms
    - warning signs

    Returns the best matching diseases rather than assuming
    that symptoms prove a diagnosis.
    """

    query_normalized = _normalize_text(query)
    query_words = _tokens(query)

    scored = []

    for disease in diseases:
        score = 0

        disease_name = disease.get("name", "")
        description = disease.get("description", "")

        # ----------------------------------------------------
        # Disease-name match
        # ----------------------------------------------------

        name_normalized = _normalize_text(disease_name)

        if name_normalized in query_normalized:
            score += 10

        # ----------------------------------------------------
        # Description match
        # ----------------------------------------------------

        description_words = _tokens(description)
        score += len(query_words & description_words)

        # ----------------------------------------------------
        # Common symptoms
        # ----------------------------------------------------

        for symptom in disease.get("common_symptoms", []):
            score += _symptom_matches(query, symptom) * 4

        # ----------------------------------------------------
        # Warning signs
        # ----------------------------------------------------

        for warning in disease.get("warning_signs", []):
            score += _symptom_matches(query, warning) * 2

        # ----------------------------------------------------
        # Keep diseases with meaningful matches
        # ----------------------------------------------------

        if score > 0:
            scored.append(
                (score, disease)
            )

    # Highest score first
    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        disease
        for score, disease in scored[:limit]
    ]


def find_disease(query: str):
    """
    Backward-compatible helper.

    Returns the single best matching disease.
    """
    matches = find_diseases(query, limit=1)

    if matches:
        return matches[0]

    return None


def create_context(disease):
    """Convert one disease record into clean text for Gemini."""

    if not disease:
        return None

    symptoms = "\n".join(
        f"- {symptom}"
        for symptom in disease.get(
            "common_symptoms",
            []
        )
    )

    warning_signs = "\n".join(
        f"- {warning}"
        for warning in disease.get(
            "warning_signs",
            []
        )
    )

    prevention = "\n".join(
        f"- {item}"
        for item in disease.get(
            "prevention",
            []
        )
    )

    context = f"""
Disease: {disease.get("name", "Unknown")}

Description:
{disease.get("description", "Not available")}

Common symptoms:
{symptoms}

Warning signs:
{warning_signs}

Prevention:
{prevention}

When to seek medical care:
{disease.get("when_to_seek_medical_care", "Not available")}

Important safety notes:
{chr(10).join("- " + x for x in disease.get("critical_safety_notes", []))}

Source:
{disease.get("source", {}).get("name", "Not available")}

Source URL:
{disease.get("source", {}).get("url", "Not available")}
"""

    return context.strip()


def create_contexts(diseases_list):
    """Create combined RAG context for multiple diseases."""

    if not diseases_list:
        return None

    contexts = []

    for disease in diseases_list:
        context = create_context(disease)

        if context:
            contexts.append(context)

    return "\n\n-------------------------\n\n".join(
        contexts
    )


# ------------------------------------------------------------
# Local RAG test
# ------------------------------------------------------------

if __name__ == "__main__":

    questions = [
        "What are the symptoms of dengue?",
        "I have fever and headache",
        "I have chills and fever",
        "I have severe abdominal pain",
    ]

    for question in questions:

        print("\n================================")
        print("QUESTION:", question)
        print("================================")

        matches = find_diseases(
            question,
            limit=3
        )

        if not matches:
            print("No relevant disease found.")
            continue

        for disease in matches:
            print(
                "MATCH:",
                disease["name"]
            )