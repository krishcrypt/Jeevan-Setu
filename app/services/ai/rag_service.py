import json
from pathlib import Path


# Location of our healthcare dataset
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

def find_disease(query: str):
    query_lower = query.lower()

    # Common names of diseases in different languages/scripts
    disease_aliases = {
        "dengue": [
            "dengue",
            "डेंगू",
            "डेंग्यू",
        ],
    }

    for disease in diseases:
        disease_name = disease["name"].lower()

        # First check the original English disease name
        if disease_name in query_lower:
            return disease

        # Then check multilingual aliases
        aliases = disease_aliases.get(disease_name, [])

        for alias in aliases:
            if alias.lower() in query_lower:
                return disease

    return None 


def create_context(disease):
    """Convert disease data into clean text for Gemini."""

    if not disease:
        return None

    symptoms = "\n".join(
        f"- {symptom}"
        for symptom in disease.get("common_symptoms", [])
    )

    prevention = "\n".join(
        f"- {item}"
        for item in disease.get("prevention", [])
    )

    context = f"""
Disease: {disease["name"]}

Description:
{disease.get("description", "Not available")}

Common symptoms:
{symptoms}

Prevention:
{prevention}

Source:
{disease["source"]["name"]}

Source URL:
{disease["source"]["url"]}
"""

    return context.strip()


# Test
if __name__ == "__main__":

    question = "What are the symptoms of dengue?"

    disease = find_disease(question)

    if disease:
        context = create_context(disease)

        print("\n===== RAG CONTEXT =====\n")
        print(context)

    else:
        print("No relevant disease found.")