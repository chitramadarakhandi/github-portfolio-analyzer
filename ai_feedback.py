# 


import os
from openai import OpenAI

client = None

if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def fallback_ai(score_data):

    score = score_data["total_score"]

    strengths = []
    weaknesses = []
    improvements = []

    if score >= 80:
        strengths.append("Strong engineering portfolio with good technical signals.")
    elif score >= 60:
        strengths.append("Decent GitHub presence with moderate technical depth.")
    else:
        weaknesses.append("Profile lacks strong engineering depth.")

    if score_data["repo_count"] < 5:
        weaknesses.append("Limited number of substantial projects.")

    if len(score_data["languages"]) < 2:
        weaknesses.append("Low tech stack diversity.")

    if score_data["stars"] == 0:
        weaknesses.append("No visible community engagement or project traction.")

    improvements.append("Add structured README sections: Problem, Architecture, Tech Stack, Impact.")
    improvements.append("Maintain consistent commit history.")
    improvements.append("Include deployment links and testing files.")
    improvements.append("Work on at least one high-impact real-world project.")

    return f"""
## AI Recruiter Evaluation (Deterministic Mode)

### Strengths
{'• ' + '\n• '.join(strengths) if strengths else '• None strongly detected'}

### Weaknesses
{'• ' + '\n• '.join(weaknesses) if weaknesses else '• Minor weaknesses detected'}

### Actionable Improvement Plan
• {'\n• '.join(improvements)}

### Final Recommendation
Improve documentation quality and add real-world impact projects to increase recruiter confidence.
"""



def generate_ai_feedback(score_data):

    if client is None:
        return fallback_ai(score_data)

    prompt = f"""
You are a senior technical recruiter evaluating a candidate’s GitHub profile.

Score: {score_data['total_score']}
Breakdown: {score_data['breakdown']}
Repo Count: {score_data['repo_count']}
Languages Used: {score_data['languages']}
Total Stars: {score_data['stars']}

Provide:
- Strengths
- Weaknesses
- Red Flags
- Actionable Improvement Plan
- Final Hiring Recommendation
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception:
        return fallback_ai(score_data)
