import boto3
import json

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def analyze_logs(log_text: str):
    """Analyse les logs CI/CD avec Claude sur Bedrock"""
    prompt = f"""You are a CI/CD Expert, Analyze this CI/CD log and identify the failure cause.
Respond ONLY with valid JSON in this exact format:
{{
    "cause": "brief description of the error",
    "step": "which step failed",
    "suggestion": "how to fix it"
}}

Log:
{log_text[:3000]}
"""
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    
    try:
        response = client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=body
        )
        
        response_body = json.loads(response["body"].read())
        
        # Extraire le texte de la réponse
        content = response_body.get("content", [{}])[0].get("text", "{}")
        
        # Parser le JSON de la réponse
        return json.loads(content)
    except Exception as e:
        return {
            "cause": "Analysis failed",
            "step": "AI processing",
            "suggestion": f"Error: {str(e)}"
        }