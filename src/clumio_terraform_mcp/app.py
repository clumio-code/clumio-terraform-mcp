from fastmcp import FastMCP
from typing import Any
from clumio_terraform_mcp import models, utils, constants

# Initialize MCP server
mcp = FastMCP("Clumio Terraform Provider MCP Server")

# MCP Tools
@mcp.tool
def generate_providers(
    clumio_accounts: list[models.ClumioAccount], 
    aws_accounts: list[models.AWSAccount]
) -> str:
    """Generate Terraform configuration for Provider blocks of Clumio and AWS."""
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
    """Generate Terraform configuration for Clumio AWS connection.
    
    Args:
        connection_name: Name for the connection resource
        description: Description of the AWS account connection
        services: Dictionary of services to enable (e.g., ebs, rds, s3, dynamodb)
        clumio_provider_alias: Alias name for Clumio provider
        aws_provider_alias: Alias name for AWS provider
        wait_for_data_plane_resources: Flag to indicate wait for data plane resources to be created
        wait_for_ingestion: Flag to indicate wait for ingestion to complete
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
    """Generate a Clumio policy for backup configuration.
    
    Args:
        policy_name: Resource name for the policy
        display_name: Human-readable name
        operations: List of operation types and settings for policy
        clumio_provider_alias: Alias name for Clumio provider
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
    storage_classes: list[str] = constants.DEFAULT_STORAGE_CLASSES,
    clumio_provider_alias: str | None = None,
) -> str:
    """Generate a protection group for organizing resources.
    
    Args:
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
        clumio_provider_alias: Alias name for Clumio provider
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
    """Generate an organizational unit for hierarchical management.

    Ensure that the provider for OU is set correctly. The provider configuring parent OU should be used to create child OUs.

    Args:
        ou_name: Resource name for the OU
        display_name: Human-readable name
        description: Description of the organizational unit
        parent_name: Reference to parent OU (If not provided, defaults to root level)
        clumio_provider_alias: Alias name for Clumio provider
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
    """Generate a policy rule to apply protection policies to resources.
    
    Args:
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
        clumio_provider_alias: Alias name for Clumio provider. Note that policy rules can be created, edited or deleted only by global admin or immediate child OU admins. Which means it doesn't allow providers that configured with grandchild OUs
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
    """Generate user assignment configuration.
    
    Args:
        clumio_provider_alias: Alias name for Clumio provider
        user_name: Resource name for the user
        email: User's email address
        full_name: User's full name
        access_control_configuration: List of access control configurations
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
def generate_report_configuration(
    config_name: str,
    config_display_name: str,
    email_list: list[str],
    controls: models.ComplianceControl,
    filters: models.ComplianceFilter,
    schedule: models.Schedule,
    clumio_provider_alias: str | None = None,
) -> str:
    """Generate compliance report configuration.
    
    Args:
        clumio_provider_alias: Alias name for Clumio provider
        config_name: Resource name for the report configuration
        config_display_name: User-friendly display name for the report
        email_list: List of email addresses to notify the report run
        controls: Compliance controls to evaluate policy or assets for compliance
        filters: Compliance filters to apply
        schedule: Schedule for the report
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

if __name__ == "__main__":
    mcp.run()
