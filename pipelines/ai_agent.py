import boto3, json

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def analyze_logs(log_text: str):
    prompt = f"""
    You are a DevOps assistant. Analyze this CI/CD log, find the cause of failure, 
    and suggest a fix in JSON format with keys: cause, step, suggestion.
    Log:
    {log_text[:4000]}
    """
    response = client.invoke_model(
        modelId="anthropic.claude-3-sonnet",
        body=json.dumps({"inputText": prompt})
    )
    output = json.loads(response["body"].read())
    return output
