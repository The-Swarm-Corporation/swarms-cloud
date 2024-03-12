config {
  force               = false
  disabled_by_default = false
}


plugin "aws" {
    enabled = true
    version = "0.27.0"
    source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

rule "terraform_required_version" {
  enabled = true
}

rule "aws_resource_missing_tags" {
  enabled = true
  tags = ["Name", "Customer"]
}
