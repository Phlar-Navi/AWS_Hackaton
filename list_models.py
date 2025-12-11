import boto3

client = boto3.client("bedrock", region_name="us-east-1")

response = client.list_models()
for m in response["modelSummaries"]:
    print(m["modelName"], m["modelVersion"], m["supportedModalities"])
