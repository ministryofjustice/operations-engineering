import unittest
from unittest.mock import patch, MagicMock
import json

class TestBedrockService(unittest.TestCase):

    @patch('boto3.client')
    def test_request_model_response_from_bedrock_llama(self, mock_boto3_client):
        mock_bedrock_runtime = MagicMock()
        mock_boto3_client.return_value = mock_bedrock_runtime
        mock_response = {'body': MagicMock(read=MagicMock(return_value=json.dumps({'generation': 'mock_result'})))}
        mock_bedrock_runtime.invoke_model.return_value = mock_response
        bedrock_service = BedrockService()
        prompt = 'test_prompt'
        model = 'llama'

        result = bedrock_service.request_model_response_from_bedrock(prompt, model)

        mock_bedrock_runtime.invoke_model.assert_called_once_with(
            modelId=LLAMA_MODEL_ID,
            body=json.dumps({'prompt': prompt, 'temperature': 0.5, 'top_p': 0.9, 'max_gen_len': 2048})
        )
        self.assertEqual(result, 'mock_result')

    @patch('boto3.client')
    def test_request_model_response_from_bedrock_claude(self, mock_boto3_client):
        mock_bedrock_runtime = MagicMock()
        mock_boto3_client.return_value = mock_bedrock_runtime
        mock_response = {'body': MagicMock(read=MagicMock(return_value=json.dumps({'content': [{'text': 'mock_result'}]})))}
        mock_bedrock_runtime.invoke_model.return_value = mock_response
        bedrock_service = BedrockService()
        prompt = 'test_prompt'
        model = 'claude'

        result = bedrock_service.request_model_response_from_bedrock(prompt, model)

        mock_bedrock_runtime.invoke_model.assert_called_once_with(
            modelId=CLAUDE_MODEL_ID,
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'system': 'Generate only the tests, with no additional speech or explanation.',
                'messages': [{'role': 'user', 'content': [{'type': 'text', 'text': prompt}]}],
                'max_tokens': 2048,
                'temperature': 0.1,
                'top_k': 250,
                'top_p': 1
            })
        )
        self.assertEqual(result, 'mock_result')

    def test_format_claude_request(self):
        bedrock_service = BedrockService()
        prompt = 'test_prompt'

        result = bedrock_service.format_claude_request(prompt)

        expected_result = {
            'anthropic_version': 'bedrock-2023-05-31',
            'system': 'Generate only the tests, with no additional speech or explanation.',
            'messages': [{'role': 'user', 'content': [{'type': 'text', 'text': prompt}]}],
            'max_tokens': 2048,
            'temperature': 0.1,
            'top_k': 250,
            'top_p': 1
        }
        self.assertEqual(result, expected_result)

    def test_format_llama_request(self):
        bedrock_service = BedrockService()
        prompt = 'test_prompt'

        result = bedrock_service.format_llama_request(prompt)

        expected_result = {
            'prompt': prompt,
            'temperature': 0.5,
            'top_p': 0.9,
            'max_gen_len': 2048
        }
        self.assertEqual(result, expected_result)
