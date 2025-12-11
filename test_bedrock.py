import boto3
import json
from dotenv import load_dotenv

load_dotenv()

client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Exemple de log CI/CD pour tester
sample_log = """
[2024-10-15 10:23:45] Starting build process...
[2024-10-15 10:23:50] Running npm install
[2024-10-15 10:24:12] ERROR: Cannot find module 'express'
[2024-10-15 10:24:12] npm ERR! code MODULE_NOT_FOUND
[2024-10-15 10:24:12] Build failed with exit code 1
"""

def test_claude_haiku():
    """Test avec Claude 3 Haiku"""
    print("🧪 Testing Claude 3 Haiku...")
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [
            {
                "role": "user",
                "content": f"""Analyze this CI/CD log and respond with JSON:
{{"cause": "error description", "step": "failed step", "suggestion": "fix"}}

Log:
{sample_log}"""
            }
        ]
    })
    
    try:
        response = client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body
        )
        
        response_body = json.loads(response["body"].read())
        content = response_body["content"][0]["text"]
        
        print("✅ SUCCESS!")
        print(f"\n📄 Raw Response:\n{content}")
        
        # Parser le JSON
        result = json.loads(content.strip().strip("```json").strip("```"))
        print(f"\n📊 Parsed JSON:")
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_mistral_large():
    """Test avec Mistral Large (alternative)"""
    print("\n🧪 Testing Mistral Large...")
    
    body = json.dumps({
        "prompt": f"Analyze this log and return JSON with cause, step, suggestion:\n{sample_log}",
        "max_tokens": 512,
        "temperature": 0.3
    })
    
    try:
        response = client.invoke_model(
            modelId="mistral.mistral-large-2402-v1:0",
            body=body
        )
        
        response_body = json.loads(response["body"].read())
        print("✅ SUCCESS!")
        print(json.dumps(response_body, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AWS Bedrock Model Testing")
    print("=" * 60)
    
    # Test Claude Haiku (recommandé)
    haiku_success = test_claude_haiku()
    
    # Si Haiku échoue, essayer Mistral
    if not haiku_success:
        print("\n⚠️  Claude Haiku failed, trying Mistral Large...")
        test_mistral_large()
    
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
    print("=" * 60)