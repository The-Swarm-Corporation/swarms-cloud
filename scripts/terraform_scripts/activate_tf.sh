#!/bin/bash

# Script to apply Terraform configuration with enhanced logging and error handling
# Define the directory where your Terraform scripts are located
TERRAFORM_DIR="/swarms-cloud/scripts/terraform_scripts/multi_cloud_consul/main.tf"

# Define the log file path
LOG_FILE="/var/log/terraform_apply.log"

# Function to log messages with timestamps
log() {
    echo "[$(date +"%Y-%m-%d %T")] $1" >> "$LOG_FILE"
}

# Ensure the Terraform directory exists
if [ ! -d "$TERRAFORM_DIR" ]; then
    log "The specified Terraform directory does not exist: $TERRAFORM_DIR"
    exit 1
fi

# Navigate to the Terraform directory
cd "$TERRAFORM_DIR" || exit

# Begin Terraform process
log "Starting Terraform apply..."

# Initialize Terraform
terraform init >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "Terraform init failed."
    exit 1
else
    log "Terraform init succeeded."
fi

# Apply Terraform configuration
terraform apply -auto-approve >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "Terraform apply failed."
    exit 1
else
    log "Terraform apply succeeded."
fi

log "Terraform apply completed successfully."

# Add cron job if it doesn't exist
CRON_JOB="0 3 * * * /path/to/terraform_apply.sh"
( crontab -l | grep -Fv terraform_apply.sh ; echo "$CRON_JOB" ) | crontab -
log "Cron job for Terraform apply script ensured."
