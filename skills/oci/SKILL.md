---
name: oci
description: "Manage Oracle Cloud Infrastructure via the OCI CLI. Use when the mission involves OCI compute, networking, storage, IAM, or any Oracle Cloud service."
---

# OCI CLI

Use this skill when the mission requires managing Oracle Cloud Infrastructure resources.

## Prerequisites

- OCI CLI must be installed and configured (`~/.oci/config`).
- Config requires: `user`, `fingerprint`, `key_file`, `tenancy`, `region`.
- Verify before starting: `oci iam region list` (confirms auth works)

## Authentication methods

| Method | When to use | Flag |
|--------|------------|------|
| API Key | Local dev, CI/CD | Default from `~/.oci/config` |
| Instance Principal | Apps on OCI compute | `--auth instance_principal` |
| Resource Principal | Functions, Data Flow | `--auth resource_principal` |
| Session Token | SSO/MFA | `oci session authenticate` first |

Use `--profile $NAME` to switch between config profiles.

## Workflow

1. **Verify auth** — `oci iam region list`
2. **Identify compartment** — Almost every command needs `--compartment-id`. List with `oci iam compartment list --compartment-id $TENANCY_OCID`.
3. **Read first** — `list`, `get` commands before mutations.
4. **Mutate** — `create`, `update`, `delete` commands.
5. **Verify** — Confirm state change.

## Output and filtering

```bash
# Default is JSON. Use --output table for readable output.
oci compute instance list -c $C --output table

# JMESPath query for specific fields
oci compute instance list -c $C --query 'data[*].{"Name":"display-name","State":"lifecycle-state","ID":id}' --output table

# Raw output (strips quotes, useful for scripting)
oci compute instance list -c $C --query 'data[0].id' --raw-output

# Auto-paginate all results
oci compute instance list -c $C --all
```

## Common operations

**Compute:**
```bash
oci compute instance list --compartment-id $C
oci iam availability-domain list --compartment-id $C
oci compute instance launch --compartment-id $C --availability-domain $AD --shape VM.Standard.E4.Flex --subnet-id $SUBNET --image-id $IMAGE --display-name "my-instance"
oci compute instance action --instance-id $ID --action STOP
oci compute instance action --instance-id $ID --action START
oci compute instance terminate --instance-id $ID --preserve-boot-volume true
```

**Networking:**
```bash
oci network vcn create --compartment-id $C --cidr-block "10.0.0.0/16" --display-name "my-vcn" --dns-label "myvcn"
oci network vcn list --compartment-id $C
oci network subnet create --compartment-id $C --vcn-id $VCN --cidr-block "10.0.1.0/24" --display-name "my-subnet"
oci network subnet list --compartment-id $C --vcn-id $VCN
oci network internet-gateway create --compartment-id $C --vcn-id $VCN --is-enabled true
oci network security-list list --compartment-id $C --vcn-id $VCN
oci network nsg create --compartment-id $C --vcn-id $VCN --display-name "app-nsg"
```

**Object Storage:**
```bash
oci os bucket list --compartment-id $C
oci os bucket create --compartment-id $C --name "my-bucket"
oci os object put --bucket-name "my-bucket" --file /path/to/file
oci os object get --bucket-name "my-bucket" --name "object-name" --file /path/to/output
oci os object list --bucket-name "my-bucket"
```

**Block Storage:**
```bash
oci bv volume list --compartment-id $C
oci bv volume create --compartment-id $C --availability-domain $AD --size-in-gbs 100 --display-name "my-volume"
oci compute volume-attachment attach --instance-id $ID --volume-id $VOL --type paravirtualized
```

**IAM:**
```bash
oci iam compartment list --compartment-id $TENANCY_OCID
oci iam user list --compartment-id $TENANCY_OCID
oci iam group list --compartment-id $TENANCY_OCID
oci iam policy list --compartment-id $C
oci iam policy create --compartment-id $C --name "my-policy" --description "desc" --statements '["Allow group Admins to manage all-resources in compartment MyCompartment"]'
```

## OCI-specific gotchas

- **VCN CIDR is immutable.** Always start with /16. Too small = create a new VCN and migrate.
- **Security List limit:** Max 5 per subnet. Use Network Security Groups (NSGs) for granular rules.
- **VCN peering is non-transitive.** Every pair needs explicit peering.
- **IAM policy propagation:** 10-60 second delay. A 404 may mean "not yet authorized," not "not found."
- **Permission hierarchy:** `inspect < read < use < manage`.
- **Service limits:** 87% of "out of capacity" errors are service limit issues. Check with `oci limits resource-availability get`.
- **Load balancers need /24 subnets minimum.**
- **CLI syntax updates monthly** — for uncommon commands, verify against `oci <service> <resource> <action> --help`.

## Guardrails

- Always verify auth first with `oci iam region list`.
- Always pass `--compartment-id` explicitly.
- Use `--all` for paginated results to avoid missing data.
- Use `--query` to limit output size.
- Use `--preserve-boot-volume true` when terminating instances unless you intend data loss.
- Use `--force` only when absolutely necessary (skips confirmation).
- Never delete VCNs or subnets that still have attached resources.
