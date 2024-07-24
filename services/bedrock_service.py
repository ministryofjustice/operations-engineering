import boto3, json

class BedrockService:
    def __init__(self) -> None:
        self.client = boto3.client("bedrock", region_name="eu-west-2")

    def make_request(self, prompt):

        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name="eu-west-2",
        )
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        model_kwargs = {
            "max_tokens": 2048,
            "temperature": 0.1,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\n\nHuman"],
        }

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "system": "Generate only the tests, with no additional speech or explanation.",
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt}]},
            ],
        }
        body.update(model_kwargs)

        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
        )

        result = json.loads(response.get("body").read()).get("content", [])[0].get("text", "")

        return result
