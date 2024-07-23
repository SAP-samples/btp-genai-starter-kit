# Step 1: Setup infrastructure
echo "###########################################################################################"
echo "Setting up SAP BTP infrastructure"
echo "--------------------------------------------------------------------------------"
cd scripts/step01_setup_infra

echo "Done."
echo "--------------------------------------------------------------------------------"
echo "Initializing terraform"
echo "--------------------------------------------------------------------------------"
terraform init
# Check if the 'terraform init' command was successful
status=$?
[ $status -eq 1 ] && echo "The 'terraform init' command was not successful. Exiting." && exit
echo "Done."

echo "--------------------------------------------------------------------------------"
echo "Applying terraform script"
echo "--------------------------------------------------------------------------------"
terraform apply -var-file="../../config/secrets/my_btp_credentials.tfvars" -var-file="../../config/secrets/my_btp_ai_setup.tfvars" --auto-approve
# Check if the 'terraform apply' command was successful
status=$?
[ $status -eq 1 ] && echo "The 'terraform apply' command was not successful. Exiting." && exit
echo "Done."

echo "--------------------------------------------------------------------------------"
echo "Prepare the AI Core service"
echo "--------------------------------------------------------------------------------"
cd ..
cd step02_deploy_models
poetry install
poetry run python main.py
