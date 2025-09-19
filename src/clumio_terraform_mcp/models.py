from pydantic import BaseModel, Field, model_validator
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
    """Model for Clumio provider configuration."""
    alias: str | None = Field(default=None, description="The alias for the Clumio provider. This is used to reference the provider in Terraform.")
    ou_name: str | None = Field(default=None, description="The name of the organizational unit resource for the Clumio account. If not specified, consider using the default organizational unit.")


class AssumeRole(BaseModel):
    """Model for AWS assume role for AWS provider configuration."""
    role_arn: str = Field(description="The ARN of the role to assume.")
    session_name: str | None = Field(default=None, description="The name of the session to create.")
    external_id: str | None = Field(default=None, description="An optional external ID to include in the assume role request.")


class AWSAccount(BaseModel):
    """Model for AWS provider configuration."""
    alias: str | None = Field(default=None, description="The alias for the AWS provider. This is used to reference the provider in Terraform.")
    region: str | None = Field(default=None, description="The AWS region for the account. If not provided, defaults to 'us-west-2'.")
    profile: str | None = Field(default=None, description="The pre-configured AWS profile to use for authentication.")
    assume_role: AssumeRole | None = Field(default=None, description="The assume role configuration for the AWS provider.")


class TimeUnit(BaseModel):
    """Model for time unit."""
    value: int
    unit: Literal['minutes', 'hours', 'days', 'weeks', 'months', 'years']


class AssetBackupControl(BaseModel):
    """Model for asset backup control parameters."""
    look_back_period: TimeUnit
    minimum_retention_duration: TimeUnit
    window_size: TimeUnit


class AssetProtectionControl(BaseModel):
    """Model for asset protection control parameters."""
    should_ignore_deactivated_policy: bool


class PolicyControl(BaseModel):
    """Model for policy control parameters."""
    minimum_retention_duration: TimeUnit
    minimum_rpo_frequency: TimeUnit


class ComplianceControl(BaseModel):
    """The set of controls supported in compliance report."""
    asset_backup: AssetBackupControl
    asset_protection: AssetProtectionControl
    policy: PolicyControl


class Group(BaseModel):
    """The group structure for asset filter."""
    group_id: str | None = None
    region: str | None = Field(default=None, description="The region of asset group. For example, us-west-2. This is supported for AWS asset groups only")
    asset_type: Literal['aws'] = 'aws'


class AssetFilter(BaseModel):
    """The set of asset filter parameters for compliance report."""
    groups: list[Group] = Field(default=[], description="The list of asset groups to be included in the report")
    tag_op_mode: Literal['and', 'or', 'equal'] | None = Field(description="The tag filter operation to be applied for the given tags. This is supported for AWS assets only")
    tags: list[dict[str, str]] = Field(default=[], description="The asset tags to be filtered. This is supported for AWS assets only")


class CommonFilter(BaseModel):
    """The set of common filter parameters for compliance report."""
    asset_types: list[CommonFilterAssetTypes] = Field(default=[], description="The asset types to be included in the report")
    data_sources: list[Literal['aws']] = Field(default=['aws'], description="The data sources to be included in the report")
    organizational_units: list[str] = Field(default=[], description="The organizational units to be included in the report")


class ComplianceFilter(BaseModel):
    """The set of filter parameters for compliance report."""
    asset: AssetFilter | None = None
    common: CommonFilter | None = None


class Schedule(BaseModel):
    """The schedule parameters for compliance report."""
    day_of_month: int = 1
    day_of_week: Literal['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] = 'monday'
    frequency: Literal['daily', 'weekly', 'monthly'] = 'daily'
    start_time: str = '00:00'
    timezone: str = 'UTC'


class SLA(BaseModel):
    """The SLAs model for policy."""
    retention_duration: TimeUnit
    rpo_frequency: TimeUnit


class ProtectionGroupBackup(BaseModel):
    """S3 protection group backup settings."""
    backup_tier: Literal['standard', 'archive'] = 'standard'


class ProtectionGroupContinuousBackup(BaseModel):
    """S3 protection group continuous backup settings."""
    disable_eventbridge_notification: bool = True


class EBSVolumeBackupAS(BaseModel):
    """Advanced Settings Configuration settings for EBS Backup."""
    backup_tier: Literal['standard', 'lite'] = 'standard'


class EC2InstanceBackupAS(BaseModel):
    """Advanced Settings Configuration settings for EC2 Instance."""
    backup_tier: Literal['standard', 'lite'] = 'standard'


class RDSPitrBackupAS(BaseModel):
    """Advanced Settings Configuration settings for RDS PITR Backup."""
    apply: Literal['immediate', 'maintenance_window'] = 'immediate'


class RdsBackupTier(BaseModel):
    """Advanced Settings Configuration settings for RDS Instance."""
    backup_tier: Literal['standard', 'archive'] = 'archive'


class AdvancedSettings(BaseModel):
    """Sub-Policy advanced settings."""
    # S3 protection group backup
    protection_group_backup: ProtectionGroupBackup | None = None
    protection_group_continuous_backup: ProtectionGroupContinuousBackup | None = None
    # EBS EC2 Backup
    aws_ebs_volume_backup: EBSVolumeBackupAS | None = None
    aws_ec2_instance_backup: EC2InstanceBackupAS | None = None
    # RDS Granular Backup
    aws_rds_resource_granular_backup: RdsBackupTier | None = None
    # RDS Pitr Backup
    aws_rds_config_sync: RDSPitrBackupAS | None = None

    def generate_advanced_settings(self):
        """Return a nested dictionary of advanced settings."""
        settings = {}
        if self.protection_group_backup:
            settings["protection_group_backup"] = {
                "backup_tier": self.protection_group_backup.backup_tier
            }
        if self.protection_group_continuous_backup:
            settings["protection_group_continuous_backup"] = {
                "disable_eventbridge_notification": self.protection_group_continuous_backup.disable_eventbridge_notification
            }
        if self.aws_ebs_volume_backup:
            settings["aws_ebs_volume_backup"] = {
                "backup_tier": self.aws_ebs_volume_backup.backup_tier
            }
        if self.aws_ec2_instance_backup:
            settings["aws_ec2_instance_backup"] = {
                "backup_tier": self.aws_ec2_instance_backup.backup_tier
            }
        if self.aws_rds_resource_granular_backup:
            settings["aws_rds_resource_granular_backup"] = {
                "backup_tier": self.aws_rds_resource_granular_backup.backup_tier
            }
        if self.aws_rds_config_sync:
            settings["aws_rds_config_sync"] = {
                "apply": self.aws_rds_config_sync.apply
            }
        return settings


class BackupWindow(BaseModel):
    """Backup window model."""
    end_time: str = '08:00'  # 8:00 AM (use empty string for no end time)
    start_time: str = '20:00'  # 8:00 PM


class Operation(BaseModel):
    """The operation model for policy."""
    type: PolicyOperationType
    action_setting: Literal['immediate', 'window'] = 'immediate'
    slas: list[SLA]
    advanced_settings: AdvancedSettings | None = None
    backup_aws_region: str | None = None
    backup_window_tz: BackupWindow | None = None
    timezone: str | None = None


class AccessControlConfiguration(BaseModel):
    """Access control configuration for a user."""
    role_name: Literal['Super Admin', 'Organizational Unit Admin', 'Helpdesk Admin'] = Field(description="Role type assigned to the user.")
    organizational_unit_ids: list[str] = Field(default=["00000000-0000-0000-0000-000000000000"], description="List of OU IDs to assign the user to. Use '00000000-0000-0000-0000-000000000000' as global OU id.")
