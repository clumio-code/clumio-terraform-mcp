import pytest
from fastmcp import Client
from clumio_terraform_mcp import app
import uuid

@pytest.fixture(scope="module")
def mcp_server():
    # Use the actual server from app
    return app.mcp

@pytest.mark.asyncio
async def test_generate_providers_tool(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("generate_providers", {
            "clumio_accounts": [
                {
                    "alias": "clumio",
                },
                {
                    "alias": "test",
                    "ou_name": "test_ou"
                }
            ],
            "aws_accounts": [
                {
                    "alias": "prod", 
                    "region": "us-east-1", 
                    "assume_role": {"role_arn": "arn"}
                },
                {
                    "alias": "dev", 
                    "region": "us-east-1", 
                    "profile": "test"
                }
            ],
        })
        assert isinstance(result.data, str)
        assert "terraform" in result.data

@pytest.mark.asyncio
async def test_generate_aws_connection_tool(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("generate_aws_connection", {
            "clumio_provider_alias": "test",
            "connection_name": "test",
            "description": "desc",
            "services": {"ebs": True, "rds": False, "s3": True, "dynamodb": False},
            "aws_provider_alias": "test",
            "wait_for_data_plane_resources": True,
            "wait_for_ingestion": True,
        })
        assert isinstance(result.data, str)
        assert "clumio_aws_connection" in result.data

@pytest.mark.asyncio
async def test_generate_policy_tool(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("generate_policy", {
            "clumio_provider_alias": "test",
            "policy_name": "test_policy",
            "display_name": "Test Policy",
            "operations": [{
                "type": "aws_ebs_volume_backup",
                "slas": [{
                    "retention_duration": {
                        "unit": "days",
                        "value": 7
                    },
                    "rpo_frequency": {
                        "unit": "days",
                        "value": 1
                    }
                }]
            }]
        })
        assert isinstance(result.data, str)
        assert "resource" in result.data

@pytest.mark.asyncio
async def test_generate_protection_group_tool(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("generate_protection_group", {
            "clumio_provider_alias": "test",
            "group_name": "test_group",
            "display_name": "Test Group",
            "policy_name": "test_policy",
            "description": "desc",
            "bucket_rule": {"aws_tag": {"$eq": {"key": "k", "value": "v"}}}
        })
        assert isinstance(result.data, str)
        assert "resource" in result.data

@pytest.mark.asyncio
async def test_generate_organizational_unit_tool(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("generate_organizational_unit", {
            "clumio_provider_alias": "test",
            "ou_name": "test_ou",
            "display_name": "OU",
            "description": "desc"
        })
        assert isinstance(result.data, str)
        assert "resource" in result.data

@pytest.mark.asyncio
async def test_generate_policy_rule_tool(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("generate_policy_rule", {
            "clumio_provider_alias": "test",
            "rule_name": "rule",
            "display_name": "Rule",
            "policy_name": "policy",
            "condition_expression": {"aws_tag": {"$eq": {"key": "k", "value": "v"}}}
        })
        assert isinstance(result.data, str)
        assert "resource" in result.data

@pytest.mark.asyncio
async def test_generate_user_assignment_tool(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("generate_user_assignment", {
            "clumio_provider_alias": "test",
            "user_name": "user",
            "email": "user@example.com",
            "full_name": "User",
            "access_control_configuration": [
                {
                    "role_name": "Super Admin",
                    "organizational_unit_ids": ["00000000-0000-0000-0000-000000000000"]
                },
                {
                    "role_name": "Helpdesk Admin",
                    "organizational_unit_ids": [str(uuid.uuid4())]
                }
            ]
        })
        assert isinstance(result.data, str)
        assert "resource" in result.data
