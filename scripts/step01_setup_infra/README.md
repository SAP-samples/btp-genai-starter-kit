# Setting up a sub account with the SAP AI Core service deployed

## Overview

This script shows how to create a SAP BTP subaccount with the `SAP AI Core` service deployed

## Content of setup

The setup comprises the following resources:

- Creation of a SAP BTP subaccount
- Entitlement of the SAP AI Core service
- Entitlement and setup of SAP HANA Cloud (incl. hana cloud tools)
- Role collection assignments to users

## Deploying the resources

To deploy the resources you must:

1. Export the variables for user name and password

   ```bash
   export BTP_USERNAME='<Email address of your BTP user>'
   export BTP_PASSWORD='<Password of your BTP user>'
   ```

2. Change the variables in the `samples.tfvars` file to meet your requirements

3. Initialize your workspace:

   ```bash
   terraform init
   ```

4. You can check what Terraform plans to apply based on your configuration:

   ```bash
   terraform plan -var-file="sample.tfvars"
   ```

5. Apply your configuration to provision the resources:

   ```bash
   terraform apply -var-file="sample.tfvars"
   ```

## In the end

You probably want to remove the assets after trying them out to avoid unnecessary costs. To do so execute the following command:

```bash
terraform destroy
```
