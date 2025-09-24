# Example Prompts for Using the Clumio Terraform MCP Server

This document provides example prompts you can use with AI assistants (Claude, ChatGPT, etc.) to generate Clumio Terraform configurations.

## AWS Connection

### Multi-Service Connection
```
Create a Terraform configuration to connect my AWS account to Clumio with:
- All backup services enabled (EBS, RDS, S3, DynamoDB)
- Region: us-west-2
- Description: "Multi-service production environment"
```

## Protection Policies

### Critical Resources Policy
```
Generate a Clumio protection policy for critical EBS volumes with:
- 90-day retention
- 1-hour RPO
- Backup window: 2 AM to 6 AM EST
- Name it "critical-data-policy"
```

### Tiered Protection Policies
```
Generate three protection policies for different SLAs:
1. Critical: 1-hour RPO, 90-day retention
2. Standard: 24-hour RPO, 30-day retention  
3. Archive: Weekly backups, 1-year retention
```

## Protection Groups

### Tag-Based Groups
```
Create a protection group that includes all resources tagged with:
- Environment = Production
- Department = Finance
Name it "finance-prod-resources"
```

## Complete Solutions

### Multi-Account Enterprise Setup
```
Generate a complete Clumio backup solution for:
- 3 AWS accounts: Production (us-east-1), Staging (us-west-2), Development (eu-west-1)
- Production: All services, 90-day retention, 1-hour RPO
- Staging: EBS and RDS only, 30-day retention, 24-hour RPO
- Development: EBS only, 7-day retention, daily backups
- Create organizational units for each environment
- Add admin users for each OU
```

### Disaster Recovery Setup
```
Generate a DR-ready Clumio configuration:
- Primary region: us-east-1
- DR region: us-west-2
- Critical resources: 15-minute RPO, cross-region replication
- Standard resources: 4-hour RPO, local backups only
- Include all database and storage services
```

## Report Configurations

### Compliance Reporting
```
Generate a compliance report configuration for daily monitoring:
- Email notifications: admin@company.com, compliance@company.com
- Asset backup control: 7-day lookback, 1-day window, 7-day minimum retention
- Asset protection: Do not ignore deactivated policies
- Policy control: 7-day minimum retention, daily minimum RPO
- Asset types: EBS volumes, RDS instances, EC2 instances
- Tag filter: Environment = Production
- Schedule: Daily at 8:00 AM EST
```

## Tips for Effective Prompts

1. **Be Specific**: Include exact retention periods, RPO values, and service names
2. **Provide Context**: Mention compliance requirements, business needs, or technical constraints
3. **Request Validation**: Ask for the configuration to be validated against best practices
4. **Iterate**: Start simple and add complexity based on the generated output
5. **Include Examples**: Reference existing resources or naming conventions

## Troubleshooting Common Issues

### Issue: Policy Creation Fails
**Solution:** Ensure all required SLA parameters (retention_duration and rpo_frequency) are specified with valid units and values.

### Issue: AWS Connection Module Errors
**Solution:** Ensure all required service flags are explicitly set (true/false) rather than omitted.

## Combining Multiple Tools

### Complete Workflow Example
```
Using the Clumio MCP server, create a complete backup infrastructure:
1. Generate AWS connection for production account
2. Create critical protection policy with 30-day retention, daily backups
3. Set up protection group for Environment=Production tags
4. Generate policy rule to automatically apply critical policy to production resources
```

### Step-by-Step Enterprise Setup
```
Create an end-to-end backup solution:
1. AWS Connections: Create connections for prod, staging, dev environments
2. Policies: Generate tiered policies (critical, standard, archive) with appropriate retention
3. Protection Groups: Set up department-based groups (Finance, Engineering, Operations)
4. Policy Rules: Create automatic assignment rules based on tags
5. Validation: Check the complete configuration and provide recommendations
```

Remember: The MCP server can handle complex, multi-step configurations. Don't hesitate to ask for comprehensive solutions that address your specific backup and compliance needs.