import unittest
from unittest.mock import patch, MagicMock
from clumio_terraform_mcp import client

class TestClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from unittest.mock import AsyncMock
        self.mock_client = MagicMock()
        self.mock_result = MagicMock()
        self.mock_result.data = 'mocked_data'
        self.mock_client.call_tool = AsyncMock(return_value=self.mock_result)

    async def test_demo_aws_connection(self):
        self.mock_client.call_tool.return_value = self.mock_result
        result = await client.demo_aws_connection(self.mock_client)
        self.assertEqual(result, 'mocked_data')
        self.mock_client.call_tool.assert_called_with('generate_aws_connection', unittest.mock.ANY)

    async def test_demo_policy(self):
        self.mock_client.call_tool.return_value = self.mock_result
        result = await client.demo_policy(self.mock_client)
        self.assertEqual(result, 'mocked_data')
        self.mock_client.call_tool.assert_called_with('generate_policy', unittest.mock.ANY)

    async def test_demo_protection_group(self):
        self.mock_client.call_tool.return_value = self.mock_result
        result = await client.demo_protection_group(self.mock_client)
        self.assertEqual(result, 'mocked_data')
        self.mock_client.call_tool.assert_called_with('generate_protection_group', unittest.mock.ANY)

    async def test_demo_organizational_unit(self):
        self.mock_client.call_tool.return_value = self.mock_result
        result = await client.demo_organizational_unit(self.mock_client)
        self.assertEqual(result, 'mocked_data')
        self.mock_client.call_tool.assert_called_with('generate_organizational_unit', unittest.mock.ANY)

    async def test_demo_policy_rule(self):
        self.mock_client.call_tool.return_value = self.mock_result
        result = await client.demo_policy_rule(self.mock_client)
        self.assertEqual(result, 'mocked_data')
        self.mock_client.call_tool.assert_called_with('generate_policy_rule', unittest.mock.ANY)

    async def test_demo_complete_solution(self):
        self.mock_client.call_tool.return_value = self.mock_result
        with patch('builtins.open', unittest.mock.mock_open()):
            result = await client.demo_complete_solution(self.mock_client)
        self.assertEqual(result, 'mocked_data')
        self.mock_client.call_tool.assert_called_with('generate_complete_backup_solution', unittest.mock.ANY)

    async def test_demo_report_configuration(self):
        self.mock_client.call_tool.return_value = self.mock_result
        result = await client.demo_report_configuration(self.mock_client)
        self.assertEqual(result, 'mocked_data')
        self.mock_client.call_tool.assert_called_with('generate_report_configuration', unittest.mock.ANY)

    async def test_demo_validation(self):
        self.mock_result.data = {'is_valid': True, 'errors': [], 'warnings': [], 'recommendations': []}
        self.mock_client.call_tool.return_value = self.mock_result
        result = await client.demo_validation(self.mock_client)
        self.assertEqual(result, self.mock_result.data)
        self.mock_client.call_tool.assert_called_with('validate_terraform_config', unittest.mock.ANY)

    async def test_demo_example_scenarios(self):
        self.mock_result.data = {'scenarios': [], 'integration_examples': {}}
        self.mock_client.call_tool.return_value = self.mock_result
        result = await client.demo_example_scenarios(self.mock_client)
        self.assertEqual(result, self.mock_result.data)
        self.mock_client.call_tool.assert_called_with('get_example_scenarios', {})

if __name__ == '__main__':
    unittest.main()
