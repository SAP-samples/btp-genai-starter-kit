#!/bin/bash
# Step 1: Destroy infrastructure
echo "--------------------------------------------------------------------------------"
echo "Cleaning up SAP BTP infrastructure"
echo "--------------------------------------------------------------------------------"
cd scripts/step01_setup_infra
terraform destroy -var-file="../../config/secrets/my_btp_credentials.tfvars" -var-file="../../config/secrets/my_btp_ai_setup.tfvars"  --auto-approve
echo "--------------------------------------------------------------------------------"
echo "Cleaning up metadata files"
echo "--------------------------------------------------------------------------------"
# Step 2: Cleanup metadata
cd ../..
./cleanup_code.sh
echo "Done!"
