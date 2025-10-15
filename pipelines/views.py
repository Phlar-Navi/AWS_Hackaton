from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from .ai_agent import analyze_logs


from django.http import JsonResponse
from .services.github_service import get_github_logs, retry_github_workflow

class AnalyzeLogs(APIView):
    def post(self, request):
        logs = request.data.get("logs", "")
        result = analyze_logs(logs)
        return Response(result)

def analyze(request):
    repo = request.GET.get("repo")
    run_id = request.GET.get("run_id")
    logs = get_github_logs(repo, run_id)
    return JsonResponse({"logs": logs})


def retry(request):
    repo = request.GET.get("repo")
    run_id = request.GET.get("run_id")
    status, text = retry_github_workflow(repo, run_id)
    return JsonResponse({"status": status, "response": text})
