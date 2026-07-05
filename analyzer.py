import os

SKIP = {".git", "node_modules", "__pycache__", "venv"}

def detect_framework(files):
    if "requirements.txt" in files:
        return "Python (Flask/Django)"
    if "package.json" in files:
        return "Node.js / React"
    if "manage.py" in files:
        return "Django"
    if "app.py" in files:
        return "Flask"
    return "Unknown"

def analyze_project(path, url):

    files_set = set()
    total_files, total_dirs, total_lines = 0, 0, 0
    langs = {}

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP]
        total_dirs += len(dirs)

        for f in files:
            files_set.add(f.lower())
            total_files += 1

            ext = os.path.splitext(f)[1]
            langs[ext] = langs.get(ext, 0) + 1

            try:
                with open(os.path.join(root, f), "r", errors="ignore") as file:
                    total_lines += len(file.readlines())
            except:
                pass

    return {
        "framework": detect_framework(files_set),
        "project_type": "Software Project",
        "summary": "Repository analyzed successfully.",
        "insights": ["Code analyzed"],
        "score": 75,
        "quality": "Good",
        "health": "Stable",
        "language_percentages": langs,
        "repo_stats": {
            "total_files": total_files,
            "total_folders": total_dirs,
            "total_lines": total_lines
        }
    }