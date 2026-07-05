import os

def search_repo(path, query):
    results = []

    for root, _, files in os.walk(path):
        for f in files:
            try:
                with open(os.path.join(root, f), "r", errors="ignore") as file:
                    for i, line in enumerate(file):
                        if query.lower() in line.lower():
                            results.append({
                                "file": f,
                                "line_number": i+1,
                                "code": line.strip()
                            })
            except:
                pass

    return results