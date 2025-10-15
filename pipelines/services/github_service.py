import requests
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_github_logs(repo, run_id):
    """
    Récupère les logs d'un workflow GitHub Actions
    """
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.text
    else:
        return f"Error {r.status_code}: {r.text}"


def retry_github_workflow(repo, run_id):
    """
    Redéclenche un workflow GitHub Actions
    """
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/rerun"
    r = requests.post(url, headers=headers)
    return r.status_code, r.text
