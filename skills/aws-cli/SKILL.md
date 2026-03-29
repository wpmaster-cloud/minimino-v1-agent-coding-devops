---
name: aws-cli
description: "Manage AWS resources via the AWS CLI. Use when the mission involves EC2, S3, IAM, Lambda, ECS, CloudWatch, or any AWS service."
---

# AWS CLI

Use this skill when the mission requires managing AWS infrastructure or services.

## Prerequisites

- AWS CLI v2 must be installed.
- Credentials configured via `~/.aws/credentials`, env vars (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`), or instance role.
- Verify before starting: `aws sts get-caller-identity`

## Workflow

1. **Verify identity** — `aws sts get-caller-identity`. Confirm account and role.
2. **Pin region and profile** — Always use `--region` and `--profile` explicitly on every command.
3. **Read first** — Use `describe-*`, `list-*`, `get-*` commands before any mutations.
4. **Dry-run when possible** — Use `--dry-run` (EC2, S3) to validate permissions.
5. **Mutate** — `create-*`, `update-*`, `put-*` commands.
6. **Wait** — Use `aws <service> wait <condition>` instead of polling loops.
7. **Verify** — Confirm the change took effect.

## Output and filtering

```bash
# JSON output (default, best for parsing)
aws ec2 describe-instances --output json | jq '.Reservations[].Instances[].InstanceId'

# JMESPath query (built-in, avoids jq dependency)
aws ec2 describe-instances --query 'Reservations[].Instances[].[InstanceId,State.Name]' --output table

# Text output (single values)
aws sts get-caller-identity --query Account --output text

# Disable pager in scripts
export AWS_PAGER=""
```

## Common operations

**IAM:**
```bash
aws iam list-users
aws iam list-roles
aws iam get-policy --policy-arn $ARN
aws iam create-role --role-name $NAME --assume-role-policy-document file://trust.json
aws iam attach-role-policy --role-name $NAME --policy-arn $ARN
aws sts assume-role --role-arn $ARN --role-session-name $SESSION
```

**EC2:**
```bash
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"
aws ec2 run-instances --image-id $AMI --instance-type t3.micro --key-name $KEY --subnet-id $SUBNET --count 1
aws ec2 terminate-instances --instance-ids $ID
aws ec2 describe-security-groups --group-ids $SG
aws ec2 wait instance-running --instance-ids $ID
```

**S3:**
```bash
aws s3 ls
aws s3 ls s3://bucket/prefix/
aws s3 cp file.txt s3://bucket/key
aws s3 sync ./dir s3://bucket/prefix/
aws s3api get-bucket-policy --bucket $BUCKET
```

**Lambda:**
```bash
aws lambda list-functions
aws lambda get-function-configuration --function-name $NAME
aws lambda invoke --function-name $NAME --payload '{}' /dev/stdout
aws lambda update-function-code --function-name $NAME --zip-file fileb://code.zip
```

**ECS:**
```bash
aws ecs list-clusters
aws ecs describe-services --cluster $CLUSTER --services $SERVICE
aws ecs list-tasks --cluster $CLUSTER --service-name $SERVICE
aws ecs update-service --cluster $CLUSTER --service $SERVICE --desired-count 2
```

**CloudWatch:**
```bash
aws logs describe-log-groups
aws logs filter-log-events --log-group-name $GROUP --filter-pattern "ERROR" --start-time $EPOCH_MS
aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization --dimensions Name=InstanceId,Value=$ID --start-time $START --end-time $END --period 300 --statistics Average
```

## Guardrails

- Always run `aws sts get-caller-identity` first.
- Always pass `--region` and `--profile` explicitly. Never rely on implicit defaults.
- Use `--dry-run` where supported before mutating.
- Never run `s3 rm --recursive` or bulk `terminate-instances` without explicit confirmation.
- Use `--query` to limit output size — full API responses can flood the context window.
- Use `--filters` for server-side filtering on large result sets (cheaper than client-side JMESPath).
- Some services are region-specific: ACM certs for CloudFront must be in `us-east-1`. IAM is global.
- Handle pagination: use `--max-items` and `--starting-token`, or let CLI auto-paginate.
