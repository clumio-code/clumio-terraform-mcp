from pydantic import BaseModel, Field
from typing import Literal

CommonFilterAssetTypes = Literal[
    'aws_ec2_instance',
    'aws_ebs_volume',
    'aws_rds',
    'aws_s3_bucket',
    'aws_dynamodb_table',
]

PolicyOperationType = Literal[
    'aws_ebs_volume_backup',
    'aws_ebs_volume_snapshot',
    'aws_ec2_instance_backup',
    'aws_ec2_instance_snapshot',
    'aws_rds_resource_aws_snapshot',
    'aws_rds_resource_rolling_backup',
    'aws_rds_resource_granular_backup',
    'aws_dynamodb_table_backup',
    'aws_dynamodb_table_snapshot',
    'aws_dynamodb_table_pitr',
    'protection_group_backup',
    'aws_s3_continuous_backup',
    'aws_s3_backtrack',
]

class ClumioAccount(BaseModel):
    """Clumio account to generate Clumio provider configurations."""
    alias: str | None = Field(default=None, description="The alias for the Clumio provider. This is used to reference the provider in Terraform. If there is only one provider, not need to give this.")
    ou_name: str | None = Field(default=None, description="The name of the organizational unit resource for the Clumio account. ")


class AssumeRole(BaseModel):
    """AWS assume role to set up credentials in AWS provider."""
    role_arn: str = Field(description="The ARN of the role to assume.")
    session_name: str | None = Field(default=None, description="The name of the session to create.")
    external_id: str | None = Field(default=None, description="An optional external ID to include in the assume role request.")


class AWSAccount(BaseModel):
    """AWS account to generate AWS provider configuration."""
    alias: str | None = Field(default=None, description="The alias for the AWS provider. This is used to reference the provider in Terraform.")
    region: str | None = Field(default=None, description="The AWS region for the account.", examples=["us-west-2", "ca-central-1"])
    profile: str | None = Field(default=None, description="The pre-configured AWS profile to use for authentication.")
    assume_role: AssumeRole | None = None


class TimeUnit(BaseModel):
    """Time unit."""
    value: int
    unit: Literal['minutes', 'hours', 'days', 'weeks', 'months', 'years']


class AssetBackupControl(BaseModel):
    """Control evaluating whether assets have at least one backup within each window of the specified look back period, with retention meeting the minimum required duration."""
    look_back_period: TimeUnit = Field(description="The duration prior to the compliance evaluation point to look back.")
    minimum_retention_duration: TimeUnit = Field(description="The minimum required retention duration for a backup to be considered compliant.")
    window_size: TimeUnit = Field(description="The size of each evaluation window within the look back period in which at least one compliant backup must exist.")


class AssetProtectionControl(BaseModel):
    """Control evaluating if all assets are protected with a policy or not."""
    should_ignore_deactivated_policy: bool = False


class PolicyControl(BaseModel):
    """Control evaluating if policies have a minimum backup retention and frequency."""
    minimum_retention_duration: TimeUnit
    minimum_rpo_frequency: TimeUnit


class ComplianceControl(BaseModel):
    """Compliance controls to evaluate policy or assets for compliance."""
    asset_backup: AssetBackupControl
    asset_protection: AssetProtectionControl
    policy: PolicyControl


class Group(BaseModel):
    """The asset groups to be filtered."""
    group_id: str | None = None
    region: str | None = Field(default=None, description="This is supported for AWS asset groups only.", examples=["us-west-2", "ca-central-1"])
    asset_type: Literal['aws'] = 'aws'


class AssetFilter(BaseModel):
    """The filter for asset. This will be applied to asset backup and asset protection controls."""
    groups: list[Group] = []
    tag_op_mode: Literal['and', 'or', 'equal'] | None = Field(description="The tag filter operation to be applied for the given tags. This is supported for AWS assets only")
    tags: list[dict[str, str]] = Field(default=[], description="The asset tags to be filtered. This is supported for AWS assets only")


class CommonFilter(BaseModel):
    """The filter for common controls. This will be applied to all controls."""
    asset_types: list[CommonFilterAssetTypes] = []
    data_sources: list[Literal['aws']] = ['aws']
    organizational_units: list[str] = []


class ComplianceFilter(BaseModel):
    """Compliance filters to apply."""
    asset: AssetFilter | None = None
    common: CommonFilter | None = None


class Schedule(BaseModel):
    """Schedule for the report."""
    day_of_month: int = Field(default=1, ge=-1, le=28, description="Day of the month to run the report. This is required for the 'monthly' report frequency (1-28, -1 for last day)")
    day_of_week: Literal['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] = Field(default='monday', description="Day of the week to run the report. This is required for the 'weekly' report frequency.")
    frequency: Literal['daily', 'weekly', 'monthly'] = 'daily'
    start_time: str = '00:00'
    timezone: str = Field(default='UTC', description="The timezone in which the report will be generated. This is in IANA format.")


class SLA(BaseModel):
    """The service level agreement (SLA) for the policy operation."""
    retention_duration: TimeUnit
    rpo_frequency: TimeUnit


class BackupWindow(BaseModel):
    """The start and end times for the customized backup window that reflects the user-defined timezone."""
    end_time: str = '08:00'  # 8:00 AM
    start_time: str = '20:00'  # 8:00 PM


class Operation(BaseModel):
    """The operation model for policy."""
    type: PolicyOperationType = Field(description="The type of operation to be performed. Depending on the type selected, advanced_settings may also be required.")
    slas: list[SLA]
    backup_aws_region: str | None = Field(default=None, description="The region in which this backup is stored. It defaults to in-region.", examples=["us-west-2", "ca-central-1"])
    backup_window_tz: BackupWindow | None = None
    timezone: str | None = Field(default=None, description="The timezone in which the backup window is defined. This should be in IANA format.")

    def generate_advanced_setting(self):
        """Return a nested dictionary of advanced setting."""
        settings = {}
        if self.type == 'protection_group_backup':
            settings["protection_group_backup"] = {"backup_tier": "standard"}
        if self.type == 'protection_group_continuous_backup':
            settings["protection_group_continuous_backup"] = {"disable_eventbridge_notification": True}
        if self.type == 'aws_ebs_volume_backup':
            settings["aws_ebs_volume_backup"] = {"backup_tier": "standard"}
        if self.type == 'aws_ec2_instance_backup':
            settings["aws_ec2_instance_backup"] = {"backup_tier": "standard"}
        if self.type == 'aws_rds_resource_granular_backup':
            settings["aws_rds_resource_granular_backup"] = {"backup_tier": "standard"}
        if self.type == 'aws_rds_config_sync':
            settings["aws_rds_config_sync"] = {"apply": "immediate"}
        return settings


class AccessControlConfiguration(BaseModel):
    """Access control configuration for a user."""
    role_name: Literal['Super Admin', 'Organizational Unit Admin', 'Helpdesk Admin'] = Field(description="Role type assigned to the user.")
    organizational_unit_ids: list[str] = Field(default=["00000000-0000-0000-0000-000000000000"], description="List of OU IDs to assign the user to. Use '00000000-0000-0000-0000-000000000000' as global OU id.")
