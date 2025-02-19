# Enable AWS secrets engine
path "sys/mounts/aws" {
  capabilities = ["create", "update"]
}

# Configure AWS secrets engine with root credentials
path "aws/config/root" {
  capabilities = ["create", "update"]
  data = {
    access_key = "<ACCESS_KEY>"
    secret_key = "<SECRET_ACCESS_KEY>"
    region     = "us-east-1"
  }
}

# Create a Vault AWS role that generates IAM user credentials
path "aws/roles/dev-role" {
  capabilities = ["create", "update"]
  data = {
    credential_type = "iam_user"
    policy_arn      = "<IAM Policy ARN>"
    max_ttl         = "24h"
    ttl             = "1h"
  }
}
