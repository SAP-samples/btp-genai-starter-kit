# ------------------------------------------------------------------------------------------------------
# Prepare & setup the SAP AI Core service (ensure your global account has the respective entitlements)
# ------------------------------------------------------------------------------------------------------
terraform {
  required_providers {
    btp = {
      source  = "sap/btp"
      version = "~> 1.16.1"
    }
  }
}
# ------------------------------------------------------------------------------------------------------
# Prepare the list of admins and roles for the AI Launchpad
# ------------------------------------------------------------------------------------------------------
locals {
  role_mapping_admins_ai_launchpad = distinct(flatten([
    for admin in var.admins : [
      for role in var.roles_ai_launchpad : {
        user_name = admin
        role_name = role
      }
    ]
    ]
  ))
}

# Entitle subaccount for usage of SAP AI Core service
# ------------------------------------------------------------------------------------------------------
# Checkout https://github.com/SAP-samples/btp-service-metadata/blob/main/v0/developer/aicore.json for 
# available plans and their region availability 
resource "btp_subaccount_entitlement" "ai_core" {
  subaccount_id = var.subaccount_id
  service_name  = "aicore"
  plan_name     = var.ai_core_plan_name
}

# Get plan for SAP AI Core service
data "btp_subaccount_service_plan" "ai_core" {
  subaccount_id = var.subaccount_id
  offering_name = "aicore"
  name          = var.ai_core_plan_name
  depends_on    = [btp_subaccount_entitlement.ai_core]
}

# Create service instance for SAP AI Core service
resource "btp_subaccount_service_instance" "ai_core" {
  subaccount_id  = var.subaccount_id
  serviceplan_id = data.btp_subaccount_service_plan.ai_core.id
  name           = "my-ai-core-instance"
  depends_on     = [btp_subaccount_entitlement.ai_core]
}

# Create service binding to SAP AI Core service (exposed for a specific user group)
resource "btp_subaccount_service_binding" "ai_core_binding" {
  subaccount_id       = var.subaccount_id
  service_instance_id = btp_subaccount_service_instance.ai_core.id
  name                = "ai-core-key"
}

# ------------------------------------------------------------------------------------------------------
# Prepare & setup SAP AI Launchpad
# ------------------------------------------------------------------------------------------------------
resource "btp_subaccount_entitlement" "ai_launchpad" {
  count = var.switch_setup_ai_launchpad ? 1 : 0

  subaccount_id = var.subaccount_id
  service_name  = "ai-launchpad"
  plan_name     = "standard"
}

resource "btp_subaccount_subscription" "ai_launchpad" {
  count = var.switch_setup_ai_launchpad ? 1 : 0

  subaccount_id = var.subaccount_id
  app_name      = "ai-launchpad"
  plan_name     = "standard"
  depends_on    = [btp_subaccount_entitlement.ai_launchpad]
}

# Assign users to Role Collection of SAP AI Launchpad
resource "btp_subaccount_role_collection_assignment" "ai_launchpad_role_mapping" {

  for_each = { for entry in local.role_mapping_admins_ai_launchpad : "${entry.user_name}.${entry.role_name}" => entry
  if var.switch_setup_ai_launchpad == true }

  subaccount_id        = var.subaccount_id
  role_collection_name = each.value.role_name
  user_name            = each.value.user_name
  depends_on           = [btp_subaccount_subscription.ai_launchpad]
}
