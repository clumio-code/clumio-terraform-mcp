# Providers
terraform {
  required_providers {
    clumio = {
      source  = "clumio-code/clumio"
    }
    aws = {}
  }
}

provider "clumio" {
  clumio_api_token    = var.clumio_api_token
  clumio_api_base_url = var.clumio_api_base_url
}

provider "aws" {
  region = var.aws_region
}

variable "clumio_api_token" {
  description = "Clumio API Token"
  type        = string
  sensitive   = true
}

variable "clumio_api_base_url" {
  description = "Clumio API Base URL"
  type        = string
}

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-west-2"
}

# AWS Account Connections
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

resource "clumio_aws_connection" "connection" {
  account_native_id = data.aws_caller_identity.current.account_id
  aws_region        = data.aws_region.current.region
  description       = "AWS connection for backup protection"
}

module "clumio_aws_resources" {
  providers = {
    aws    = aws
    clumio = clumio
  }
  source                = "clumio-code/aws-template/clumio"
  clumio_token          = clumio_aws_connection.connection.token
  role_external_id      = clumio_aws_connection.connection.role_external_id
  aws_region            = clumio_aws_connection.connection.aws_region
  aws_account_id        = clumio_aws_connection.connection.account_native_id
  clumio_aws_account_id = clumio_aws_connection.connection.clumio_aws_account_id

  # Service enablement flags
  is_ebs_enabled        = true
  is_rds_enabled        = true
  is_s3_enabled         = true
  is_dynamodb_enabled   = true
}


# Policies
resource "clumio_policy" "unified_policy" {
  name              = "Unified Policy"
  activation_status = "activated"
  operations {
    action_setting = "immediate"
    type           = "aws_ec2_instance_backup"
    slas {
      retention_duration {
        unit  = "days"
        value = 30
      }
      rpo_frequency {
        unit  = "days"
        value = 1
      }
    }
    advanced_settings {
      aws_ec2_instance_backup {
        backup_tier = "standard"
      }
    }
  }
  operations {
    action_setting = "immediate"
    type           = "aws_ebs_volume_backup"
    slas {
      retention_duration {
        unit  = "days"
        value = 30
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
  operations {
    action_setting = "immediate"
    type           = "aws_dynamodb_table_backup"
    slas {
      retention_duration {
        unit  = "days"
        value = 30
      }
      rpo_frequency {
        unit  = "days"
        value = 1
      }
    }
    slas {
      retention_duration {
        unit  = "days"
        value = 3
      }
      rpo_frequency {
        unit  = "hours"
        value = 6
      }
    }
  }
  operations {
    action_setting = "immediate"
    type           = "aws_rds_resource_rolling_backup"
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
  }
  operations {
    action_setting = "immediate"
    type           = "protection_group_backup"
    slas {
      retention_duration {
        unit  = "months"
        value = 3
      }
      rpo_frequency {
        unit  = "days"
        value = 1
      }
    }
    advanced_settings {
      protection_group_backup {
        backup_tier = "standard"
      }
    }
  }
}


# Protection Groups
resource "clumio_protection_group" "s3_protection_group" {
  name           = "S3 Protection Group"
  description    = "Protection Group for S3 buckets tagged with backup:true"
  bucket_rule    = jsonencode(
    {
      "aws_tag": {
        "$eq": {
          "key": "backup",
          "value": "true"
        }
      }
    }
  )
  object_filter {
    storage_classes = ["S3 Standard", "S3 Standard-IA", "S3 Intelligent-Tiering", "S3 One Zone-IA", "S3 Reduced Redundancy"]
  }
}

resource "clumio_policy_assignment" "s3_protection_group_assignment" {
  entity_id   = clumio_protection_group.s3_protection_group.id
  entity_type = "protection_group"
  policy_id   = clumio_policy.unified_policy.id
}

# Policy Rules
resource "clumio_policy_rule" "unified_protection_rule" {
  policy_id           = clumio_policy.unified_policy.id
  name                = "Unified Protection Rule"
  before_rule_id      = ""
  condition = jsonencode(
    {
      "aws_tag": {
        "$eq": {
          "key": "backup",
          "value": "true"
        }
      },
      "entity_type": {
        "$in": [
          "aws_ec2_instance",
          "aws_ebs_volume",
          "aws_dynamodb_table",
          "aws_rds_instance",
          "aws_rds_cluster"
        ]
      }
    }
  )
}

