import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_latest_workflow_run(repo):
    """Récupère l'ID du dernier workflow run"""
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    
    r = requests.get(
        f"https://api.github.com/repos/{repo}/actions/runs",
        headers=headers
    )
    r.raise_for_status()
    
    data = r.json()
    if data["workflow_runs"]:
        return data["workflow_runs"][0]["id"]
    return None