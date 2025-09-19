from fastmcp import FastMCP
from typing import Any, Final
from clumio_terraform_mcp import models, utils

DEFAULT_STORAGE_CLASSES: Final = [
    "S3 Standard", 
    "S3 Standard-IA", 
    "S3 Intelligent-Tiering", 
    "S3 One Zone-IA", 
    "S3 Reduced Redundancy"
]

# Initialize MCP server
mcp = FastMCP("Clumio Terraform Provider MCP Server")

# MCP Tools
@mcp.tool
def generate_providers(
    clumio_accounts:list[models.ClumioAccount], 
    aws_accounts: list[models.AWSAccount]
) -> str:
    """
    Generate Terraform configuration for Provider blocks of Clumio and AWS.

    Args:
        clumio_accounts: List of Clumio accounts to generate provider configurations for. Each account may include:
            alias: The alias for the Clumio provider.
            ou_name: The name of the organizational unit resource for the Clumio account. If not specified, consider using the default organizational unit.
        aws_accounts: List of AWS accounts to generate provider configurations for. Each account may include:
            alias: The alias for the AWS provider.
            region: The AWS region for the account.
            profile: The pre-configured AWS profile to use for authentication.
            assume_role: The assume role configuration for the AWS provider.
                role_arn: The ARN of the role to assume.
                session_name: The name of the session to create.
                external_id: An optional external ID to include in the assume role request.

    Returns:
        Terraform configuration as string.
    """
    return utils.render_tf_template(
        'provider.tf.j2', clumio_accounts=clumio_accounts, aws_accounts=aws_accounts
    ).strip()

@mcp.tool
def generate_aws_connection(
    connection_name: str,
    description: str,
    services: dict[str, bool],
    clumio_provider_alias: str | None = None,
    aws_provider_alias: str | None = None,
    wait_for_data_plane_resources: bool = False,
    wait_for_ingestion: bool = False
) -> str:
    """
    Generate Terraform configuration for Clumio AWS connection.
    
    Args:
        clumio_provider_alias: Alias name for Clumio provider
        connection_name: Name for the connection resource
        description: Description of the AWS account connection
        services: Dictionary of services to enable (e.g., ebs, rds, s3, dynamodb)
        aws_provider_alias: Alias name for AWS provider
        wait_for_data_plane_resources: Flag to indicate wait for data plane resources to be created
        wait_for_ingestion: Flag to indicate wait for ingestion to complete

    Returns:
        Terraform configuration as string
    """
    return utils.render_tf_template(
        'aws_connection.tf.j2',
        clumio_provider_alias=clumio_provider_alias,
        connection_name=connection_name,
        description=description,
        services=services,
        aws_provider_alias=aws_provider_alias,
        wait_for_data_plane_resources=wait_for_data_plane_resources,
        wait_for_ingestion=wait_for_ingestion,
    ).strip()

    

@mcp.tool
def generate_policy(
    policy_name: str,
    display_name: str,
    operations: list[models.Operation],
    clumio_provider_alias: str | None = None,
) -> str:
    """
    Generate a Clumio policy for backup configuration.
    
    Args:
        clumio_provider_alias: Alias name for Clumio provider
        policy_name: Resource name for the policy
        display_name: Human-readable name
        operations: List of operation types and settings for policy
            type: The type of operation to be performed. Depending on the type selected, advanced_settings may also be required. Supported types include:
                (aws_ebs_volume_backup, aws_ebs_volume_snapshot, aws_ec2_instance_backup, aws_ec2_instance_snapshot, aws_rds_resource_aws_snapshot, aws_rds_resource_rolling_backup, aws_rds_resource_granular_backup, aws_dynamodb_table_backup, aws_dynamodb_table_snapshot, aws_dynamodb_table_pitr, protection_group_backup)
            action_setting: Determines whether the policy should take action now or during the specified backup window (immediate, window)
            slas: The service level agreement (SLA) for the policy
                slas.retention_duration: The time unit of retention duration for the policy
                slas.rpo_frequency: The time unit of recovery point objective (RPO) frequency for the policy
            advanced_settings: Additional settings for the policy
                advanced_settings.aws_ebs_volume_backup: Backup tier configuration for EBS volume backup
                advanced_settings.aws_ec2_instance_backup: Backup tier configuration for EC2 instance backup
                advanced_settings.aws_rds_config_sync: Sync configuration for RDS PITR backup
                advanced_settings.aws_rds_granular_backup: Backup tier configuration for RDS backup
                advanced_settings.protection_group_backup: Backup tier configuration for S3 protection group backup
                advanced_settings.protection_group_continuous_backup: Event bridge notification setting for S3 continuous backup
            backup_aws_region: The region in which this backup is stored. This might be used for cross-region backup. Possible values are AWS region string, for example: us-east-1, us-west-2. If no value is provided, it defaults to in-region
            backup_window_tz: The start and end times for the customized backup window that reflects the user-defined timezone
            timezone: The time zone for the policy, in IANA format. This might be set up when backup window exists
    
    Returns:
        Terraform configuration for policy
    """
    return utils.render_tf_template(
        'policy.tf.j2',
        clumio_provider_alias=clumio_provider_alias,
        policy_name=policy_name,
        display_name=display_name,
        operations=operations,
    ).strip()

@mcp.tool
def generate_protection_group(
    group_name: str,
    display_name: str,
    policy_name: str,
    description: str,
    bucket_rule: dict[str, Any],
    storage_classes: list[str] = DEFAULT_STORAGE_CLASSES,
    clumio_provider_alias: str | None = None,
) -> str:
    """
    Generate a protection group for organizing resources.
    
    Args:
        clumio_provider_alias: Alias name for Clumio provider
        group_name: Resource name for the group
        display_name: Human-readable name
        policy_name: Reference to the policy resource
        description: Description of the protection group
        bucket_rule: Configuration for bucket rule. Each rule is constructed with field, rule condition, and value. e.g., {"aws_tag": {"$eq": {"key": "Environment", "value": "Production"}}}
            Possible fields include:
            - aws_tag: Denotes the AWS tag(s) to conditionalize on
                - rule condition: $eq, $not_eq, $contains, $not_contains, $all, $not_all, $in, $not_in
            - aws_account_native_id: Denotes the AWS account to conditionalize on
                - rule condition: $eq, $in
            - aws_region: Denotes the AWS region to conditionalize on
                - rule condition: $eq, $in
        storage_classes: List of storage classes to include
    
    Returns:
        Terraform configuration for protection group
    """
    return utils.render_tf_template(
        'protection_group.tf.j2',
        clumio_provider_alias=clumio_provider_alias,
        group_name=group_name,
        display_name=display_name,
        policy_name=policy_name,
        description=description,
        bucket_rule=bucket_rule,
        storage_classes=storage_classes
    ).strip()

@mcp.tool
def generate_organizational_unit(
    ou_name: str,
    display_name: str,
    description: str,
    parent_name: str | None = None,
    clumio_provider_alias: str | None = None,
) -> str:
    """
    Generate an organizational unit for hierarchical management. Ensure that the provider for OU is set correctly.
    The provider configuring parent OU should be used to create child OUs.

    Args:
        clumio_provider_alias: Alias name for Clumio provider
        ou_name: Resource name for the OU
        display_name: Human-readable name
        description: Description of the organizational unit
        parent_name: Reference to parent OU (If not provided, defaults to root level)

    Returns:
        Terraform configuration for organizational unit
    """
    return utils.render_tf_template(
        'organizational_unit.tf.j2',
        clumio_provider_alias=clumio_provider_alias,
        ou_name=ou_name,
        display_name=display_name,
        description=description,
        parent_name=parent_name
    ).strip()

@mcp.tool
def generate_policy_rule(
    rule_name: str,
    display_name: str,
    policy_name: str,
    condition_expression: dict[str, Any],
    before_rule_name: str | None = None,
    clumio_provider_alias: str | None = None,
) -> str:
    """
    Generate a policy rule to apply protection policies to resources.
    
    Args:
        clumio_provider_alias: Alias name for Clumio provider. Note that policy rules can be created, edited or deleted only by global admin or immediate child OU admins. Which means it doesn't allow providers that configured with grandchild OUs
        rule_name: Resource name for the rule
        display_name: Human-readable name
        policy_name: Reference to the policy resource
        condition_expression: Condition configuration for applying the rule. e.g., {"aws_tag": {"$eq": {"key": "Environment", "value": "Production"}}}
            Possible fields include:
            - entity_type: Required, denotes the type of resource to apply the rule to
                - rule condition: $eq, $in
                - possible values: aws_rds_instance, aws_ebs_volume, aws_ec2_instance, aws_dynamodb_table, aws_rds_cluster
            - aws_tag: Denotes the AWS tag(s) to conditionalize on
                - rule condition: $eq, $contains, $all, $in
            - aws_account_native_id: Denotes the AWS account to conditionalize on
                - rule condition: $eq, $in
            - aws_region: Denotes the AWS region to conditionalize on
                - rule condition: $eq, $in
        before_rule_name: Reference to the rule which should run before this one

    Returns:
        Terraform configuration for policy rule
    """
    return utils.render_tf_template(
        'policy_rule.tf.j2',
        clumio_provider_alias=clumio_provider_alias,
        rule_name=rule_name,
        display_name=display_name,
        policy_name=policy_name,
        condition_expression=condition_expression,
        before_rule_name=before_rule_name
    ).strip()

@mcp.tool
def generate_user_assignment(
    user_name: str,
    email: str,
    full_name: str,
    access_control_configuration: list[models.AccessControlConfiguration],
    clumio_provider_alias: str | None = None,
) -> str:
    """
    Generate user assignment configuration.
    
    Args:
        clumio_provider_alias: Alias name for Clumio provider
        user_name: Resource name for the user
        email: User's email address
        full_name: User's full name
        access_control_configuration: List of access control configurations
            role_name: Role type (Super Admin, Organizational Unit Admin, Helpdesk Admin)
            organizational_units: List of OU IDs to assign user to
    
    Returns:
        Terraform configuration for user assignment
    """
    return utils.render_tf_template(
        'user.tf.j2',
        clumio_provider_alias=clumio_provider_alias,
        user_name=user_name,
        email=email,
        full_name=full_name,
        access_control_configuration=access_control_configuration,
    ).strip()

@mcp.tool
def generate_complete_backup_solution(config: dict[str, Any]) -> str:
    """
    Generate a complete Terraform configuration for Clumio backup solution.
    
    Args:
        config: Complete configuration including:
            - clumio_accounts: List of Clumio accounts to configure
            - aws_accounts: List of AWS accounts where resources are located
            - organizational_units: List of organizational units in Clumio
            - aws_connections: List of AWS connections in Clumio
            - policies: Backup policies by operation type
            - protection_groups: Protection groups for S3 Policy
            - policy_rules: Policy rules to resource mappings except for S3
            - users: User access configuration
    
    Returns:
        Complete Terraform configuration file
    """
    terraform_configs = []
    
    # Header and providers
    terraform_configs.append("# Providers")
    provider_config = utils.render_tf_template(
        'provider.tf.j2', 
        clumio_accounts=config.get('clumio_accounts', []),
        aws_accounts=config.get('aws_accounts', [])
    ).strip()
    terraform_configs.append(provider_config)

    # Generate organizational units
    if 'organizational_units' in config:
        terraform_configs.append("\n# Organizational Units")
        for ou in config['organizational_units']:
            ou_config = utils.render_tf_template('organizational_unit.tf.j2', **ou)
            terraform_configs.append(ou_config)
            terraform_configs.append("")

    # Generate AWS connections
    if 'aws_connections' in config:
        terraform_configs.append("\n# AWS Account Connections")
        for connection in config['aws_connections']:
            conn_config = utils.render_tf_template('aws_connection.tf.j2', **connection).strip()
            terraform_configs.append(conn_config)
            terraform_configs.append("")
    
    # Generate policies
    if 'policies' in config:
        terraform_configs.append("\n# Policies")
        for policy in config['policies']:
            policy['operations'] = [models.Operation(**op) for op in policy['operations']]
            policy_config = utils.render_tf_template('policy.tf.j2', **policy).strip()
            terraform_configs.append(policy_config)
            terraform_configs.append("")

    # Generate protection groups
    if 'protection_groups' in config:
        terraform_configs.append("\n# Protection Groups")
        for group in config['protection_groups']:
            group['storage_classes'] = group.get('storage_classes', DEFAULT_STORAGE_CLASSES)
            group_config = utils.render_tf_template(
                'protection_group.tf.j2', **group
            ).strip()
            terraform_configs.append(group_config)
    
    # Generate policy rules
    if 'policy_rules' in config:
        terraform_configs.append("\n# Policy Rules")
        for policy_rule in config['policy_rules']:
            rule_config = utils.render_tf_template(
                'policy_rule.tf.j2', **policy_rule
            ).strip()
            terraform_configs.append(rule_config)
            terraform_configs.append("")
    
    # Generate user assignments
    if 'users' in config:
        terraform_configs.append("\n# User Assignments")
        for user in config['users']:
            user_config = utils.render_tf_template(
                'user.tf.j2', **user
            ).strip()
            terraform_configs.append(user_config)
    
    terraform_configs.append("")  # Final newline
    
    return '\n'.join(terraform_configs)

@mcp.tool
def generate_report_configuration(
    config_name: str,
    config_display_name: str,
    email_list: list[str],
    controls: models.ComplianceControl,
    filters: models.ComplianceFilter,
    schedule: models.Schedule,
    clumio_provider_alias: str | None = None,
) -> str:
    """
    Generate compliance report configuration.
    
    Args:
        clumio_provider_alias: Alias name for Clumio provider
        config_name: Resource name for the report configuration
        config_display_name: User-friendly display name for the report
        email_list: List of email addresses to notify the report run
        controls: Compliance controls to evaluate policy or assets for compliance
            asset_backup: The control evaluating whether assets have at least one backup within each window of the specified look back period, with retention meeting the minimum required duration
                look_back_period: The duration prior to the compliance evaluation point to look back
                minimum_retention_duration: The minimum required retention duration for a backup to be considered compliant
                window_size: The size of each evaluation window within the look back period in which at least one compliant backup must exist
            asset_protection: The control evaluating if all assets are protected with a policy or not
                should_ignore_deactivated_policy: Treat deactivated policies as compliant if true
            policy: The control evaluating if policies have a minimum backup retention and frequency
                minimum_retention_duration: The minimum retention duration for policy control
                minimum_rpo_duration: The minimum RPO duration for policy control
        filters: Compliance filters to apply
            asset: The filter for asset. This will be applied to asset backup and asset protection controls
                groups: The asset groups to be filtered
                tag_op_mode: The tag filter operation to be applied to the given tags. This is supported for AWS assets only (and, or, equal)
                tags: The asset tags to be filtered. This is supported for AWS assets only
            common: The filter for common controls. This will be applied to all controls
                asset_types: The asset types to be included in the report. This can include:
                    (aws_ec2_instance, aws_ebs_volume, aws_rds, aws_s3_bucket, aws_dynamodb_table)
                data_sources: The data sources to be included in the report (e.g. aws)
                organizational_units: The UUID of organizational units to be included in the report
        schedule: Schedule for the report
            day_of_month: Day of the month to run the report. This is required for the 'monthly' report frequency (1-28, -1 for last day)
            day_of_week: Day of the week to run the report. This is required for the 'weekly' report frequency ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
            frequency: Frequency of the report ('daily', 'weekly', 'monthly')
            start_time: Start time for the report generation
            timezone: Timezone for the report schedule (e.g., "America/New_York")

    Returns:
        Terraform configuration for the report
    """
    return utils.render_tf_template(
        'report_configuration.tf.j2',
        clumio_provider_alias=clumio_provider_alias,
        config_name=config_name,
        config_display_name=config_display_name,
        email_list=email_list,
        controls=controls,
        filters=filters,
        schedule=schedule
    ).strip()

@mcp.tool
def validate_terraform_config(config_content: str) -> dict[str, Any]:
    """
    Validate Terraform configuration syntax and best practices.
    
    Args:
        config_content: Terraform configuration to validate
    
    Returns:
        Validation results with warnings and recommendations
    """
    validation_results = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Check for required provider configuration
    if "provider \"clumio\"" not in config_content:
        validation_results["errors"].append("Missing Clumio provider configuration")
        validation_results["is_valid"] = False
    
    if "provider \"aws\"" not in config_content and "aws" in config_content.lower():
        validation_results["warnings"].append("AWS provider may be required but not configured")
    
    # Check for sensitive variable handling
    if "clumio_api_token" in config_content and "sensitive = true" not in config_content:
        validation_results["warnings"].append("API token should be marked as sensitive")
    
    # Check for hardcoded values
    if "clumio_api_token =" in config_content and "var." not in config_content:
        validation_results["errors"].append("API token appears to be hardcoded - use variables instead")
        validation_results["is_valid"] = False
    
    # Best practice recommendations
    if "terraform {" in config_content:
        if "required_version" not in config_content:
            validation_results["recommendations"].append("Consider adding required_version constraint")
    
    if "backup_window" in config_content:
        validation_results["recommendations"].append("Ensure backup windows don't overlap with peak usage times")
    
    if "retention" in config_content:
        validation_results["recommendations"].append("Review retention policies for compliance requirements")
    
    return validation_results

# Example usage scenarios
@mcp.tool
def get_example_scenarios() -> dict[str, Any]:
    """
    Get example scenarios for using the Clumio Terraform MCP server.
    
    Returns:
        Dictionary of example scenarios with descriptions and sample configurations
    """
    return {
        "scenarios": [
            {
                "name": "Multi-Account Enterprise Setup",
                "description": "Configure Clumio for multiple AWS accounts with different protection requirements",
                "use_case": "Large enterprise with production, staging, and development accounts",
                "example_prompt": "Generate a Terraform configuration for 3 AWS accounts (prod, staging, dev) with different retention policies"
            },
            {
                "name": "Compliance-Driven Backup",
                "description": "Set up backup policies to meet regulatory compliance (HIPAA, SOC2, etc.)",
                "use_case": "Healthcare or financial services requiring specific retention and RPO",
                "example_prompt": "Create HIPAA-compliant backup policies with 7-year retention for databases"
            },
            {
                "name": "Tag-Based Protection",
                "description": "Automatically protect resources based on tags",
                "use_case": "Dynamic environments where resources are tagged by department or criticality",
                "example_prompt": "Generate protection groups for all resources tagged with Environment=Production"
            },
            {
                "name": "Disaster Recovery Setup",
                "description": "Configure cross-region backup replication",
                "use_case": "Business continuity planning with geographic redundancy",
                "example_prompt": "Set up EBS and RDS backups with replication to a DR region"
            },
            {
                "name": "Cost-Optimized Backup",
                "description": "Tiered protection based on resource importance",
                "use_case": "Cost-conscious organizations with varying data criticality",
                "example_prompt": "Create tiered backup policies: critical (1hr RPO), standard (24hr RPO), archive (weekly)"
            }
        ],
        "integration_examples": {
            "with_claude": "Ask Claude to 'Generate a Clumio backup configuration for my production AWS account with hourly EBS snapshots'",
            "with_automation": "Use in CI/CD pipelines to automatically configure backup for new AWS accounts",
            "with_chatops": "Integrate with Slack/Teams bots for on-demand backup policy creation"
        }
    }

if __name__ == "__main__":
    mcp.run()
