import unittest
from unittest.mock import patch, MagicMock
import json
from services.bedrock_service import BedrockService, LLAMA_MODEL_ID, CLAUDE_MODEL_ID

class TestBedrockService(unittest.TestCase):

    @patch('boto3.client')
    def test_request_model_response_from_bedrock_llama(self, mock_boto3_client):
        bedrock_service = BedrockService()

        # Create a mock response object
        mock_response_body = MagicMock()
        mock_response_body.read.return_value = json.dumps({"generation": "mock_result"})

        mock_response = MagicMock()
        mock_response.__getitem__.return_value = mock_response_body

        # Set up the mock boto3 client to return the mock response
        mock_boto3_client.return_value.invoke_model.return_value = mock_response

        prompt = "test_prompt"
        model = "llama"

        result = bedrock_service.request_model_response_from_bedrock(prompt, model)

        # Validate the boto3 client calls
        mock_boto3_client.assert_any_call(service_name="bedrock-runtime", region_name="eu-west-2")
        mock_boto3_client.return_value.invoke_model.assert_called_once_with(
            modelId=LLAMA_MODEL_ID,
            body=json.dumps(bedrock_service.format_llama_request(prompt))
        )

        # Check the result
        self.assertEqual(result, "mock_result")

    # @patch('boto3.client')
    # def test_request_model_response_from_bedrock_llama(self, mock_boto3_client):
    #     bedrock_service = BedrockService()
    #     mock_response = MagicMock()
    #     mock_response.get.return_value.read.return_value = json.dumps({"generation": "mock_result"})
    #     mock_boto3_client.return_value.invoke_model.return_value = mock_response
    #     prompt = "test_prompt"
    #     model = "llama"

    #     result = bedrock_service.request_model_response_from_bedrock(prompt, model)

    #     mock_boto3_client.assert_any_call("bedrock", region_name="eu-west-2")
    #     mock_boto3_client.assert_any_call("bedrock-runtime", region_name="eu-west-2")
    #     mock_boto3_client.return_value.invoke_model.assert_called_once()
    #     assert result == "mock_result"

    @patch('boto3.client')
    def test_request_model_response_from_bedrock_claude(self, mock_boto3_client):

        bedrock_service = BedrockService()

        # Create a mock response object
        mock_response_body = MagicMock()
        mock_response_body.read.return_value = json.dumps({"content": [{"text": "mock_result"}]})

        mock_response = MagicMock()
        mock_response.get.return_value = mock_response_body

        # Set up the mock boto3 client to return the mock response
        mock_boto3_client.return_value.invoke_model.return_value = mock_response

        prompt = "test_prompt"
        model = "claude"

        result = bedrock_service.request_model_response_from_bedrock(prompt, model)

        # Validate the boto3 client calls
        mock_boto3_client.assert_any_call(service_name="bedrock-runtime", region_name="eu-west-2")
        mock_boto3_client.return_value.invoke_model.assert_called_once_with(
            modelId=CLAUDE_MODEL_ID,
            body=json.dumps(bedrock_service.format_claude_request(prompt))
        )

        # Check the result
        self.assertEqual(result, "mock_result")

    # @patch('boto3.client')
    # def test_request_model_response_from_bedrock_claude(self, mock_boto3_client):
    #     bedrock_service = BedrockService()
    #     mock_response = MagicMock()
    #     mock_response.get.return_value.read.return_value = json.dumps({"content": [{"text": "mock_result"}]})
    #     mock_boto3_client.return_value.invoke_model.return_value = mock_response
    #     prompt = "test_prompt"
    #     model = "claude"

    #     result = bedrock_service.request_model_response_from_bedrock(prompt, model)

    #     mock_boto3_client.assert_any_call("bedrock", region_name="eu-west-2")
    #     mock_boto3_client.assert_any_call("bedrock-runtime", region_name="eu-west-2")
    #     mock_boto3_client.return_value.invoke_model.assert_called_once()
    #     assert result == "mock_result"

    def test_format_claude_request(self):
        bedrock_service = BedrockService()
        prompt = "test_prompt"
        expected_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "system": "Generate only the tests, with no additional speech or explanation.",
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt}]},
            ],
            "max_tokens": 4096,
            "temperature": 0.1,
            "top_k": 250,
            "top_p": 1
        }

        request = bedrock_service.format_claude_request(prompt)

        assert request == expected_request

    def test_format_llama_request(self):
        bedrock_service = BedrockService()
        prompt = "test_prompt"
        expected_request = {
            "prompt": prompt,
            "temperature": 0.5,
            "top_p": 0.9,
            "max_gen_len": 2048,
        }

        request = bedrock_service.format_llama_request(prompt)

        assert request == expected_request

    @patch('boto3.client')
    def test_init(self, mock_boto3_client):
        BedrockService()

        mock_boto3_client.assert_called_once_with("bedrock", region_name="eu-west-2")
