import boto3

class BedrockService:
    def __init__(self) -> None:
        self.client = boto3.client("bedrock", region_name="eu-west-2")

    def make_request(self, prompt):
        return "test"
