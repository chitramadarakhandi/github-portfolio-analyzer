from datetime import datetime

def calculate_score(user_data, repos):

    total_score = 0
    breakdown = {}

    # -----------------------------
    # 1️⃣ Repository Strength (Max 20)
    # -----------------------------
    repo_count = len(repos)
    repo_score = min(repo_count * 2, 20)
    breakdown["Repository Strength"] = repo_score
    total_score += repo_score


    # -----------------------------
    # 2️⃣ Documentation Quality (Max 20)
    # -----------------------------
    description_count = sum(1 for repo in repos if repo.get("description"))
    doc_score = min(description_count * 2, 20)
    breakdown["Documentation Quality"] = doc_score
    total_score += doc_score


    # -----------------------------
    # 3️⃣ Activity Recency (Max 20)
    # -----------------------------
    if repos:
        latest_update = max(repo["updated_at"] for repo in repos)
        last_date = datetime.strptime(latest_update, "%Y-%m-%dT%H:%M:%SZ")
        days_diff = (datetime.utcnow() - last_date).days

        if days_diff <= 30:
            activity_score = 20
        elif days_diff <= 90:
            activity_score = 15
        elif days_diff <= 180:
            activity_score = 10
        else:
            activity_score = 5
    else:
        activity_score = 0

    breakdown["Recent Activity"] = activity_score
    total_score += activity_score


    # -----------------------------
    # 4️⃣ Tech Stack Diversity (Max 20)
    # -----------------------------
    languages = set(repo["language"] for repo in repos if repo["language"])
    lang_score = min(len(languages) * 5, 20)
    breakdown["Tech Stack Diversity"] = lang_score
    total_score += lang_score


    # -----------------------------
    # 5️⃣ Popularity Signals (Max 20)
    # -----------------------------
    total_stars = sum(repo["stargazers_count"] for repo in repos)
    star_score = min(total_stars, 20)
    breakdown["Community Impact"] = star_score
    total_score += star_score


    return {
        "total_score": total_score,
        "breakdown": breakdown,
        "repo_count": repo_count,
        "languages": list(languages),
        "stars": total_stars
    }
