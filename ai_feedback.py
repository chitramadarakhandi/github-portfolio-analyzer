import os
from openai import OpenAI

# Initialize OpenAI client only if key exists
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------- FALLBACK (Deterministic AI) ---------------- #

def fallback_ai(score_data):

    score = score_data["total_score"]

    strengths = []
    weaknesses = []
    suggestions = []

    # -------- Strength Logic --------
    if score >= 80:
        strengths.append("Strong engineering portfolio with solid technical depth.")
    elif score >= 60:
        strengths.append("Moderate GitHub presence with good improvement potential.")
    else:
        weaknesses.append("Profile lacks strong engineering depth.")

    if score_data["repo_count"] >= 5:
        strengths.append("Good number of repositories demonstrating consistent effort.")
    else:
        weaknesses.append("Limited number of substantial projects.")

    if len(score_data["languages"]) >= 2:
        strengths.append("Healthy diversity in tech stack.")
    else:
        weaknesses.append("Low tech stack diversity.")

    if score_data["stars"] == 0:
        weaknesses.append("No visible community engagement or project traction.")
    else:
        strengths.append("Some community validation through stars.")

    # -------- Suggestions --------
    suggestions.append("Add structured README sections: Problem, Architecture, Tech Stack, Impact.")
    suggestions.append("Maintain consistent commit history across weeks.")
    suggestions.append("Include deployment links and project screenshots.")
    suggestions.append("Build at least one high-impact real-world project solving a practical problem.")

    return {
        "strengths": strengths if strengths else ["No major strengths strongly detected."],
        "weaknesses": weaknesses if weaknesses else ["No major weaknesses detected."],
        "suggestions": suggestions
    }


# ---------------- MAIN AI FUNCTION ---------------- #

def generate_ai_feedback(score_data):

    # If no OpenAI key → use fallback immediately
    if client is None:
        return fallback_ai(score_data)

    prompt = f"""
You are a senior technical recruiter evaluating a candidate’s GitHub profile.

Score: {score_data['total_score']}
Breakdown: {score_data['breakdown']}
Repo Count: {score_data['repo_count']}
Languages Used: {score_data['languages']}
Total Stars: {score_data['stars']}

Return response strictly in this JSON format:

{{
  "strengths": ["point1", "point2"],
  "weaknesses": ["point1", "point2"],
  "suggestions": ["point1", "point2", "point3", "point4"]
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        # Try to parse structured JSON response
        import json
        content = response.choices[0].message.content

        try:
            parsed = json.loads(content)
            return parsed
        except Exception:
            # If parsing fails, fallback
            return fallback_ai(score_data)

    except Exception:
        # If quota exceeded or API error → fallback safely
        return fallback_ai(score_data)
