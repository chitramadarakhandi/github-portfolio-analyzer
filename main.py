from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import requests
import os

from scoring import calculate_score
from ai_feedback import generate_ai_feedback

from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

templates = Jinja2Templates(directory="templates")

GITHUB_API = "https://api.github.com/users/"

app.mount("/static", StaticFiles(directory="static"), name="static")  #need to add this line to serve static files like CSS and JS

# ---------------- LOGIN PAGE ---------------- #

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):

    # Simple mock login
    if username == "admin" and password == "admin123":
        request.session["user"] = username
        return RedirectResponse("/dashboard", status_code=302)
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Invalid Credentials"
    })

# ---------------- DASHBOARD ---------------- #

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse("dashboard.html", {"request": request})

# ---------------- ANALYZE ---------------- #

@app.post("/analyze", response_class=HTMLResponse)
def analyze(request: Request, github_username: str = Form(...)):

    if "user" not in request.session:
        return RedirectResponse("/", status_code=302)

    user_url = GITHUB_API + github_username
    repo_url = user_url + "/repos"

    github_token = os.getenv("GITHUB_TOKEN")

    headers = {}
    if github_token:
        headers = {
            "Authorization": f"Bearer {github_token}"
        }

    user_response = requests.get(user_url, headers=headers)
    repo_response = requests.get(repo_url, headers=headers)

    if user_response.status_code != 200:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "error": "GitHub user not found or API limit exceeded."
        })

    if repo_response.status_code != 200:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "error": "Failed to fetch repositories."
        })

    user_data = user_response.json()
    repos = repo_response.json()

    if not isinstance(repos, list):
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "error": "Unexpected GitHub API response."
        })

    score_data = calculate_score(user_data, repos)
    ai_feedback = generate_ai_feedback(score_data)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "result": score_data,
        "ai_feedback": ai_feedback
    })

