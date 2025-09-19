# Clumio Terraform Provider MCP Server

<img src=".github/logo.svg" alt="Clumio" width="30%" />


A Model Context Protocol (MCP) server for the Clumio Terraform Provider that helps generate and manage Terraform configurations for the Clumio platform.

## Overview

This MCP server provides an AI-friendly interface to generate Terraform configurations for Clumio's backup-as-a-service platform. It includes tools for:

- AWS account connections
- Policies and rules
- Protection groups
- Organizational units
- User management
- Backup compliance report configurations
- Configuration validation

## Features

### Tools Available

1. **generate_providers** - Configure Clumio Provider block with variables
2. **generate_aws_connection** - Configure Clumio connections to AWS accounts
3. **generate_policy** - Create backup policies with retention and RPO settings
4. **generate_protection_group** - Define resource groups based on tags, names, or IDs
5. **generate_organizational_unit** - Build hierarchical organizational structures
6. **generate_policy_rule** - Apply policies to resources through rules
7. **generate_user_assignment** - Manage user access and permissions
8. **generate_complete_backup_solution** - Generate comprehensive backup configurations
9. **generate_report_configuration** - Create compliance report configurations
10. **validate_terraform_config** - Validate configurations for best practices
11. **get_example_scenarios** - Access common use case examples

## Installation

### Setup

1. Clone the repository:
```bash
git clone https://github.com/clumio/clumio-terraform-mcp.git
cd clumio-terraform-mcp
```

2. Install dependencies:
```bash
pip install -e .
```

3. Run the MCP server:
```bash
python src/clumio_terraform_mcp/app.py
```

## Usage

## Testing

### Install test dependencies

```bash
pip install .[test]
```

### Run all tests

```bash
pytest
```

### With the Demo Client

Run the interactive demo client to explore all features:

```bash
# Interactive mode
python src/clumio_terraform_mcp/client.py

# Run all demos
python src/clumio_terraform_mcp/client.py --all
```

### With LLMs (Claude, ChatGPT, etc.)

Ask your AI assistant to use the Clumio Terraform MCP server:

```
"Using the Clumio Terraform MCP server, generate a backup configuration for my production AWS account with:
- EBS and RDS backups enabled
- 30-day retention for critical resources
- 4-hour RPO for databases
- Tag-based protection for resources tagged Environment:Production"
```

### Example Configurations

#### 1. Basic AWS Connection

```hcl
terraform {
  required_providers {
    clumio = {
      source = "clumio-code/clumio"
      version = "~>0.15.0"
    }
    aws = {}
  }
}

provider "clumio" {
  clumio_api_token    = var.clumio_api_token
  clumio_api_base_url = var.clumio_api_base_url
}

resource "clumio_aws_connection" "production" {
  account_native_id = data.aws_caller_identity.current.account_id
  aws_region        = "us-east-1"
  description       = "Production AWS Account"
}
```

#### 2. Policy with Advanced Settings

```hcl
resource "clumio_policy" "standard_policy" {
  name        = "Standard Resources Policy"
  operations {
    action_setting = "immediate"
    type           = "aws_ebs_volume_backup"
    
    slas {
      retention_duration {
        unit  = "days"
        value = 7
      }
      
      rpo_frequency {
        unit  = "days"
        value = 1
      }
    }
    
    advanced_settings {
      aws_ebs_volume_backup {
        backup_tier = "standard"
      }
    }
  }
}
```

#### 3. Tag-Based Protection Group

```hcl
resource "clumio_protection_group" "production_databases" {
  name        = "Production Database Resources"
  description = "All production database resources"
  bucket_rule    = jsonencode({
    "aws_tag": {
      "$eq": {
        "key": "backup", 
        "value": "true"
      }
    }
  })
  object_filter {
    storage_classes = ["S3 Standard", "S3 Standard-IA", "S3 Intelligent-Tiering", "S3 One Zone-IA", "S3 Reduced Redundancy"]
  }
}
```

## Common Use Cases

### Multi-Account Enterprise Setup
Configure Clumio for multiple AWS accounts (production, staging, development) with different protection requirements.

### Compliance-Driven Backup
Set up HIPAA, SOC2, or other compliance-specific backup policies with appropriate retention periods.

### Tag-Based Protection
Automatically protect resources based on tags like Environment, Department, or Criticality.

### Disaster Recovery
Configure cross-region backup replication for business continuity.

### Cost-Optimized Backup
Implement tiered protection based on resource importance with different RPO/retention settings.

## Best Practices

1. **Use Variables for Sensitive Data**: Never hardcode API tokens or credentials
2. **Implement Hierarchical OUs**: Organize resources using organizational units
3. **Tag Resources Consistently**: Use standardized tags for automatic protection
4. **Set Appropriate Retention**: Balance compliance requirements with storage costs
5. **Configure Backup Windows**: Schedule backups during low-usage periods
6. **Validate Configurations**: Use the validation tool before applying changes

## Integration Examples

### CI/CD Pipeline Integration

```yaml
# GitHub Actions example
- name: Generate Clumio Config
  run: |
    python -c "
    from fastmcp import Client
    import asyncio
    
    async def generate():
        client = Client('app.py')
        async with client:
            result = await client.call_tool('generate_aws_connection', {
                'connection_name': 'prod',
                'description': 'Production Account',
                'services': {'ebs': True, 'rds': True}
            })
            print(result.data)
    
    asyncio.run(generate())
    " > clumio_config.tf
```

### Terraform Module Usage

```hcl
module "clumio_backup" {
  source = "./clumio-generated"
  
  clumio_api_token    = var.clumio_api_token
  clumio_api_base_url = var.clumio_api_base_url
  aws_region          = var.aws_region
}
```

## API Reference

### Tool Parameters

Each tool accepts specific parameters. Here are the key ones:

#### generate_aws_connection
- `connection_name`: Name for the connection resource
- `description`: Description of the AWS account connection
- `services`: Dictionary of services to enable (ebs, rds, s3, dynamodb)
- `aws_provider_alias`: Alias name for AWS provider
- `wait_for_data_plane_resources`: Flag to indicate wait for data plane resources to be created
- `wait_for_ingestion`: Flag to indicate wait for ingestion to complete

#### generate_policy
- `policy_name`: Resource name for the policy
- `display_name`: Human-readable name
- `operations`: List of operation types and settings for policy

#### generate_protection_group
- `group_name`: Resource name for the group
- `display_name`: Human-readable name
- `policy_name`: Reference to the policy resource
- `description`: Description of the protection group
- `bucket_rule`: Configuration for bucket rule. Each rule is constructed with field, rule condition, and value. e.g., {"aws_tag": {"$eq": {"key": "Environment", "value": "Production"}}}
- `storage_classes`: List of storage classes to include

## Example Prompts for AI Assistants

Check out [example_prompts.md](example_prompts.md) for comprehensive examples of how to use this MCP server with AI assistants like Claude or ChatGPT.

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure Clumio API token is valid and properly configured
2. **Provider Version Conflicts**: Use the recommended provider version
3. **Resource Dependencies**: Apply AWS connection before other resources
4. **Tag Format Issues**: Ensure tags are properly formatted as key-value pairs

### Debug Mode

Enable debug output by setting environment variables:
```bash
export TF_LOG=DEBUG
export CLUMIO_DEBUG=true
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

- Clumio Documentation: https://documentation.commvault.com/clumio/index.html
- Terraform Provider Docs: https://registry.terraform.io/providers/clumio-code/clumio/latest
- GitHub Issues: https://github.com/clumio/clumio-terraform-mcp/issues
