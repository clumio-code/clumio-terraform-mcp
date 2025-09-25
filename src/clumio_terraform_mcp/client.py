import asyncio
from fastmcp import Client
import sys

async def demo_aws_connection(client):
    """Demo: Generate AWS Connection configuration"""
    print("\n=== AWS Connection Configuration ===")

    result = await client.call_tool("generate_aws_connection", {
        "clumio_provider_alias": "global",
        "connection_name": "production_account",
        "description": "Production AWS Account",
        "services": {
            'ebs': True,
            'rds': True,
            's3': True,
            'dynamodb': False
        },
        "aws_provider_alias": "prod",
        "wait_for_data_plane_resources": True,
        "wait_for_ingestion": True,
    })
    
    print(result.data)
    return result.data

async def demo_policy(client):
    """Demo: Generate Policy"""
    print("\n=== Policy Configuration ===")
    
    # EBS Volume backup policy with advanced settings
    result = await client.call_tool("generate_policy", {
        "clumio_provider_alias": "global",
        "policy_name": "ebs_standard_policy",
        "display_name": "Standard EBS Volume Protection",
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
            }],
            "backup_aws_region": "us-west-2",
            "backup_window_tz": {
                "start_time": "02:00",
                "end_time": "04:00"
            },
            "timezone": "America/Los_Angeles"
        }]
    })
    
    print(result.data)
    return result.data

async def demo_protection_group(client):
    """Demo: Generate Protection Group"""
    print("\n=== Protection Group Configuration ===")
    
    # Tag-based protection group
    result = await client.call_tool("generate_protection_group", {
        "clumio_provider_alias": "global",
        "group_name": "production_databases",
        "display_name": "Production Database Resources",
        "policy_name": "ebs_standard_policy",
        "description": "All production database resources",
        "bucket_rule": {
            "aws_tag": {
                "$eq": {
                    "key": "backup",
                    "value": "true"
                }
            },
            "aws_account_native_id": {
                "$eq": "${clumio_aws_connection.prod_account.account_native_id}"
            },
            "aws_region": {
                "$eq": "${clumio_aws_connection.prod_account.aws_region}"
            }
        }
    })
    
    print(result.data)
    return result.data

async def demo_organizational_unit(client):
    """Demo: Generate Organizational Unit"""
    print("Currently Organizational Unit Configuration is disabled.")
    print("\n=== Organizational Unit Configuration ===")
    
    result = await client.call_tool("generate_organizational_unit", {
        "clumio_provider_alias": "global",
        "ou_name": "engineering_ou",
        "display_name": "Engineering Department",
        "description": "Engineering team resources and policies"
    })
    
    print(result.data)
    return result.data

async def demo_policy_rule(client):
    """Demo: Generate Policy Rule"""
    print("\n=== Policy Rule Configuration ===")
    
    result = await client.call_tool("generate_policy_rule", {
        "clumio_provider_alias": "global",
        "rule_name": "apply_critical_to_prod",
        "display_name": "Apply Critical Policy to Production",
        "policy_name": "ebs_critical_policy",
        "condition_expression": {
            "aws_tag": {
                "$eq": {
                    "key": "environment",
                    "value": "production"
                }
            }
        }
    })
    
    print(result.data)
    return result.data

async def demo_complete_solution(client):
    """Demo: Generate Complete Backup Solution"""
    print("\n=== Complete Backup Solution ===")
    
    config = {
        "clumio_accounts": [{}],
        "aws_accounts": [],
        "aws_connections": [
            {
                "connection_name": "connection",
                "description": "AWS connection for backup protection",
                "services": {
                    "ebs": True,
                    "rds": True,
                    "s3": True,
                    "dynamodb": True
                },
                "wait_for_data_plane_resources": False,
                "wait_for_ingestion": False,
            },
        ],
        "policies": [
            {
                "policy_name": "unified_policy",
                "display_name": "Unified Policy",
                "operations": [
                    {
                        "type": "aws_ec2_instance_backup",
                        "slas": [{
                            "retention_duration": {"unit": "days", "value": 30},
                            "rpo_frequency": {"unit": "days", "value": 1}
                        }]
                    },
                    {
                        "type": "aws_ebs_volume_backup",
                        "slas": [{
                            "retention_duration": {"unit": "days", "value": 30},
                            "rpo_frequency": {"unit": "days", "value": 1}
                        }]
                    },
                    {
                        "type": "aws_dynamodb_table_backup",
                        "slas": [
                            {
                                "retention_duration": {"unit": "days", "value": 30},
                                "rpo_frequency": {"unit": "days", "value": 1}
                            },
                            {
                                "retention_duration": {"unit": "days", "value": 3},
                                "rpo_frequency": {"unit": "hours", "value": 6}
                            },
                        ]
                    },
                    {
                        "type": "aws_rds_resource_rolling_backup",
                        "slas": [
                            {
                                "retention_duration": {"unit": "days", "value": 7},
                                "rpo_frequency": {"unit": "days", "value": 1}
                            }
                        ]
                    },
                    {
                        "type": "protection_group_backup",
                        "slas": [{
                            "retention_duration": {"unit": "months", "value": 3},
                            "rpo_frequency": {"unit": "days", "value": 1}
                        }]
                    },
                ]
            },
        ],
        "protection_groups": [
            {
                "group_name": "s3_protection_group",
                "display_name": "S3 Protection Group",
                "policy_name": "unified_policy",
                "description": "Protection Group for S3 buckets tagged with backup:true",
                "bucket_rule": {
                    "aws_tag": {
                        "$eq": {
                            "key": "backup",
                            "value": "true"
                        }
                    },
                }
            }
        ],
        "policy_rules": [
            {
                "rule_name": "unified_protection_rule",
                "display_name": "Unified Protection Rule",
                "policy_name": "unified_policy",
                "condition_expression": {
                    "aws_tag": {
                        "$eq": {
                            "key": "backup",
                            "value": "true"
                        }
                    },
                    "entity_type": {
                        "$in": ["aws_ec2_instance", "aws_ebs_volume", "aws_dynamodb_table", "aws_rds_instance", "aws_rds_cluster"]
                    }
                }
            }
        ]
    }
    results = []
    results.append(await client.call_tool("generate_providers", {
        "clumio_accounts": [{}],
        "aws_accounts": [],
    }))
    results.append(await client.call_tool("generate_aws_connection", config["aws_connections"][0]))
    for policy in config["policies"]:
        results.append(await client.call_tool("generate_policy", policy))
    for pg in config["protection_groups"]:
        results.append(await client.call_tool("generate_protection_group", pg))
    for pr in config["policy_rules"]:
        results.append(await client.call_tool("generate_policy_rule", pr))

    result = '\n\n'.join(r.data for r in results)

    # Save to file
    with open("complete_backup_solution.tf", "w") as f:
        f.write(result)

    print(f"Complete solution saved to complete_backup_solution.tf")
    print(f"Configuration size: {len(result)} characters")
    return result

async def demo_report_configuration(client):
    """Demo: Generate Report Configuration"""
    print("\n=== Report Configuration ===")

    config = {
        "config_name": "compliance_report",
        "config_display_name": "Daily Compliance Report",
        "email_list": ["admin@company.com", "compliance@company.com"],
        "controls": {
            "asset_backup": {
                "look_back_period": {"value": 7, "unit": "days"},
                "minimum_retention_duration": {"value": 7, "unit": "days"},
                "window_size": {"value": 1, "unit": "days"}
            },
            "asset_protection": {
                "should_ignore_deactivated_policy": False
            },
            "policy": {
                "minimum_retention_duration": {"value": 7, "unit": "days"},
                "minimum_rpo_frequency": {"value": 1, "unit": "days"}
            }
        },
        "filters": {
            "common": {
                "asset_types": ["aws_ec2_instance", "aws_ebs_volume", "aws_rds"],
                "data_sources": ["aws"],
                "organizational_units": []
            },
            "asset": {
                "tag_op_mode": "equal",
                "tags": [{"key": "Environment", "value": "Production"}],
                "groups": []
            }
        },
        "schedule": {
            "frequency": "daily",
            "start_time": "08:00",
            "timezone": "America/New_York"
        }
    }

    result = await client.call_tool("generate_report_configuration", config)
    print(result.data)
    return result.data

async def interactive_menu(client):
    """Interactive menu for demonstrations"""
    demos = {
        "1": ("AWS Connection", demo_aws_connection),
        "2": ("Policy", demo_policy),
        "3": ("Protection Group", demo_protection_group),
        "4": ("Organizational Unit", demo_organizational_unit),
        "5": ("Policy Rule", demo_policy_rule),
        "6": ("Complete Backup Solution", demo_complete_solution),
        "7": ("Report Configuration", demo_report_configuration),
        "0": ("Run All Demos", None)
    }
    
    while True:
        print("\n" + "="*50)
        print("Clumio Terraform MCP Server Demo")
        print("="*50)
        
        for key, (name, _) in demos.items():
            print(f"{key}. {name}")
        print("q. Quit")
        
        choice = input("\nSelect a demo (or 'q' to quit): ").strip().lower()
        
        if choice == 'q':
            break
        
        if choice == "0":
            # Run all demos
            for key, (name, func) in demos.items():
                if key != "0" and func:
                    print(f"\n{'='*20} Running: {name} {'='*20}")
                    await func(client)
                    input("\nPress Enter to continue...")
        elif choice in demos and demos[choice][1]:
            await demos[choice][1](client)
            input("\nPress Enter to continue...")
        else:
            print("Invalid choice. Please try again.")

async def main():
    """Main function with interactive menu"""
    client = Client("src/clumio_terraform_mcp/app.py")
    
    # Check if running with command line argument
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            # Run all demos non-interactively
            async with client:
                print("Running all demonstrations...")
                await demo_aws_connection(client)
                await demo_policy(client)
                await demo_protection_group(client)
                await demo_organizational_unit(client)
                await demo_policy_rule(client)
                await demo_complete_solution(client)
                await demo_report_configuration(client)
        elif sys.argv[1] == "--help":
            print("Usage: python src/clumio_terraform_mcp/client.py [OPTIONS]")
            print("\nOptions:")
            print("  --all     Run all demonstrations")
            print("  --help    Show this help message")
            print("\nWithout options, runs in interactive mode")
    else:
        # Interactive mode
        async with client:
            await interactive_menu(client)

if __name__ == "__main__":
    asyncio.run(main())
