from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import git, os, json

from analyzer import analyze_project
from visualizer import create_language_chart
from code_search import search_repo

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/charts", StaticFiles(directory="."), name="charts")

BASE_DIR = "repos"
CACHE = {}
os.makedirs(BASE_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

def clone_repo(repo_url):
    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_path = os.path.join(BASE_DIR, repo_name)

    os.makedirs(BASE_DIR, exist_ok=True)

    if os.path.exists(repo_path):
        return repo_path

    try:
        git.Repo.clone_from(repo_url, repo_path, depth=1, single_branch=True)
        return repo_path
    except:
        return None

@app.post("/analyze")
def analyze_repo(repo_url: str = Form(...)):
    if repo_url in CACHE:
        return CACHE[repo_url]

    path = clone_repo(repo_url)
    if not path:
        return {"error": "Clone failed"}

    result = analyze_project(path, repo_url)
    chart = create_language_chart(result["language_percentages"])
    result["language_chart"] = chart

    CACHE[repo_url] = result
    return result

@app.post("/search")
def search(repo_url: str = Form(...), query: str = Form(...)):
    name = repo_url.rstrip("/").split("/")[-1]
    path = os.path.join(BASE_DIR, name)

    if not os.path.exists(path):
        return {"error": "Analyze first"}

    return {"results": search_repo(path, query)[:20]}

@app.get("/download")
def download(repo_url: str):
    if repo_url not in CACHE:
        return {"error": "Analyze first"}

    data = CACHE[repo_url]
    name = repo_url.split("/")[-1]
    file = f"{name}.json"

    with open(file, "w") as f:
        json.dump(data, f, indent=4)

    return FileResponse(file)

# Q&A
def generate_answer(q, data):
    q = q.lower()
    stats = data["repo_stats"]

    if "framework" in q:
        return f"Framework: {data['framework']}"
    if "language" in q:
        return f"Languages: {', '.join(data['language_percentages'].keys())}"
    if "files" in q:
        return f"{stats['total_files']} files"
    if "folders" in q:
        return f"{stats['total_folders']} folders"
    if "lines" in q:
        return f"{stats['total_lines']} lines"
    return data["summary"]

@app.post("/ask")
def ask(repo_url: str = Form(...), question: str = Form(...)):
    if repo_url not in CACHE:
        return {"question": question, "answer": "Analyze first"}

    data = CACHE[repo_url]
    return {
        "question": question,
        "answer": generate_answer(question, data)
    }