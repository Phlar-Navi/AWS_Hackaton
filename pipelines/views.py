from django.http import JsonResponse
from rest_framework.decorators import api_view
from .services.github_service import get_github_logs, retry_github_workflow
from .ai_agent import analyze_logs
from .github_api import get_latest_workflow_run

@api_view(['GET'])
def get_latest_run(request):
    """Récupère l'ID du dernier workflow run"""
    repo = request.GET.get("repo")
    
    if not repo:
        return JsonResponse({"error": "repo parameter is required"}, status=400)
    
    try:
        run_id = get_latest_workflow_run(repo)
        
        if run_id:
            return JsonResponse({
                "repo": repo,
                "latest_run_id": run_id,
                "message": "Use this run_id to analyze or retry the workflow"
            })
        else:
            return JsonResponse({
                "error": "No workflow runs found for this repository"
            }, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['POST'])
def analyze(request):
    """Analyse les logs d'un workflow GitHub"""
    repo = request.data.get("repo")
    run_id = request.data.get("run_id")
    
    if not repo or not run_id:
        return JsonResponse({"error": "repo and run_id are required"}, status=400)
    
    try:
        # Récupérer les logs
        logs = get_github_logs(repo, run_id)
        
        # Analyser avec l'IA
        analysis = analyze_logs(logs)
        
        return JsonResponse({
            "repo": repo,
            "run_id": run_id,
            "analysis": analysis
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
def retry(request):
    """Redéclenche un workflow GitHub"""
    repo = request.data.get("repo")
    run_id = request.data.get("run_id")
    
    if not repo or not run_id:
        return JsonResponse({"error": "repo and run_id are required"}, status=400)
    
    try:
        status_code, response_text = retry_github_workflow(repo, run_id)
        
        return JsonResponse({
            "success": status_code == 201,
            "status_code": status_code,
            "message": "Workflow retriggered" if status_code == 201 else "Failed to retrigger",
            "response": response_text
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)