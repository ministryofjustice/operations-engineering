import unittest
from unittest.mock import patch, MagicMock
import json
from services.bedrock_service import BedrockService
from config.constants import CLAUDE_MODEL_ID, LLAMA_MODEL_ID

class TestBedrockService(unittest.TestCase):

    @patch.object(BedrockService, "format_claude_request")
    @patch("boto3.client")
    def test_request_model_response_from_bedrock_claude(self, mock_boto_client, mock_format_claude_request):
        mock_prompt = "test prompt"
        mock_model_request = {"mock": "request"}
        mock_format_claude_request.return_value = mock_model_request
        mock_response = {"body": MagicMock(read=MagicMock(return_value=json.dumps({"content": [{"text": "mock response"}]})))}
        mock_boto_client.return_value.invoke_model.return_value = mock_response

        bedrock_service = BedrockService()
        result = bedrock_service.request_model_response_from_bedrock(mock_prompt, "claude")

        mock_format_claude_request.assert_called_once_with(mock_prompt)
        mock_boto_client.return_value.invoke_model.assert_called_once_with(modelId=CLAUDE_MODEL_ID, body=json.dumps(mock_model_request))
        assert result == "mock response"

    @patch.object(BedrockService, "format_llama_request")
    @patch("boto3.client")
    def test_request_model_response_from_bedrock_llama(self, mock_boto_client, mock_format_llama_request):
        mock_prompt = "test prompt"
        mock_model_request = {"mock": "request"}
        mock_format_llama_request.return_value = mock_model_request
        mock_response = {"body": MagicMock(read=MagicMock(return_value=json.dumps({"generation": "mock response"})))}
        mock_boto_client.return_value.invoke_model.return_value = mock_response

        bedrock_service = BedrockService()
        result = bedrock_service.request_model_response_from_bedrock(mock_prompt, "llama")

        mock_format_llama_request.assert_called_once_with(mock_prompt)
        mock_boto_client.return_value.invoke_model.assert_called_once_with(modelId=LLAMA_MODEL_ID, body=json.dumps(mock_model_request))
        assert result == "mock response"

    def test_format_claude_request(self):
        mock_prompt = "test prompt"
        bedrock_service = BedrockService()
        expected_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "system": "Generate only the tests, with no additional speech or explanation.",
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": mock_prompt}]},
            ],
            "max_tokens": 4096,
            "temperature": 0.1,
            "top_k": 250,
            "top_p": 1
        }

        assert bedrock_service.format_claude_request(mock_prompt) == expected_request

    def test_format_llama_request(self):
        mock_prompt = "test prompt"
        bedrock_service = BedrockService()
        expected_request = {
            "prompt": mock_prompt,
            "temperature": 0.5,
            "top_p": 0.9,
            "max_gen_len": 2048,
        }

        assert bedrock_service.format_llama_request(mock_prompt) == expected_request
