# S3 Bucket Encryption Policy
# Ensures all S3 buckets have encryption enabled

package aws.s3.encryption

import rego.v1

# Default policy result
default allow := false

# Allow if bucket has server-side encryption enabled
allow if {
    input.resource_type == "aws_s3_bucket"
    is_encrypted
}

# Check if bucket has any form of encryption enabled
is_encrypted if {
    input.server_side_encryption_configuration[_].rule[_].apply_server_side_encryption_by_default.sse_algorithm
}

is_encrypted if {
    input.server_side_encryption_configuration[_].rule[_].apply_server_side_encryption_by_default.kms_master_key_id
}

# Violation details for non-compliant resources
violation[msg] if {
    not allow
    input.resource_type == "aws_s3_bucket"
    msg := {
        "resource_id": input.resource_id,
        "resource_type": input.resource_type,
        "policy": "s3-encryption-required",
        "severity": "high",
        "message": sprintf("S3 bucket '%s' does not have encryption enabled", [input.resource_id]),
        "remediation": "Enable server-side encryption on the S3 bucket using AES-256 or KMS encryption",
        "compliance_frameworks": ["SOC2", "PCI-DSS", "GDPR"]
    }
}

# Policy metadata
metadata := {
    "policy_id": "AWS-S3-001",
    "title": "S3 Bucket Encryption Required",
    "description": "All S3 buckets must have server-side encryption enabled",
    "severity": "high",
    "category": "data_protection"
}
