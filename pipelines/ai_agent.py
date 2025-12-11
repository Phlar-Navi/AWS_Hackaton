import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = boto3.client(
    "bedrock-runtime", 
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

def analyze_logs(log_text: str):
    """
    Analyse les logs CI/CD avec Claude 3 Haiku via AWS Bedrock
    """
    try:
        prompt = f"""You are a DevOps expert analyzing CI/CD pipeline failures.

Analyze this log and respond with ONLY valid JSON (no markdown, no explanation):

{{
    "cause": "brief description of the root cause",
    "step": "which step/job failed",
    "suggestion": "specific actionable fix"
}}

Log excerpt:
{log_text[:3500]}

JSON:"""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        response = client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",  # ON_DEMAND disponible
            body=body
        )
        
        response_body = json.loads(response["body"].read())
        
        # Extraire le contenu de la réponse
        content = response_body.get("content", [{}])[0].get("text", "")
        
        # Nettoyer la réponse (enlever markdown si présent)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Parser le JSON
        result = json.loads(content)
        
        # Valider que les clés attendues sont présentes
        if not all(key in result for key in ["cause", "step", "suggestion"]):
            raise ValueError("Missing required keys in AI response")
        
        return result
        
    except json.JSONDecodeError as e:
        return {
            "cause": "AI response parsing failed",
            "step": "JSON decoding",
            "suggestion": f"Claude returned invalid JSON. Raw response: {content[:200]}"
        }
    except Exception as e:
        return {
            "cause": "Analysis failed",
            "step": "AI processing",
            "suggestion": f"Error: {str(e)}"
        }


def analyze_logs_with_fallback(log_text: str):
    """
    Version avec fallback sur plusieurs modèles si le premier échoue
    """
    models_to_try = [
        "anthropic.claude-3-haiku-20240307-v1:0",      # Rapide et pas cher
        "anthropic.claude-3-5-sonnet-20240620-v1:0",   # Plus performant
        "mistral.mistral-large-2402-v1:0",             # Alternative
    ]
    
    for model_id in models_to_try:
        try:
            print(f"Trying model: {model_id}")
            
            prompt = f"""Analyze this CI/CD log and return only JSON:
{{"cause": "error description", "step": "failed step", "suggestion": "fix"}}

Log:
{log_text[:3000]}"""

            if "anthropic" in model_id:
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}]
                })
            elif "mistral" in model_id:
                body = json.dumps({
                    "prompt": prompt,
                    "max_tokens": 1024,
                    "temperature": 0.3
                })
            
            response = client.invoke_model(modelId=model_id, body=body)
            response_body = json.loads(response["body"].read())
            
            # Extraire contenu selon le modèle
            if "anthropic" in model_id:
                content = response_body["content"][0]["text"]
            elif "mistral" in model_id:
                content = response_body["outputs"][0]["text"]
            
            # Parser JSON
            content = content.strip().strip("```json").strip("```").strip()
            result = json.loads(content)
            
            print(f"✅ Success with {model_id}")
            return result
            
        except Exception as e:
            print(f"❌ Failed with {model_id}: {e}")
            continue
    
    # Si tous les modèles échouent
    return {
        "cause": "All AI models failed",
        "step": "AI processing",
        "suggestion": "Check AWS Bedrock permissions and model access"
    }