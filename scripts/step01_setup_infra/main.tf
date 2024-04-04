# ------------------------------------------------------------------------------------------------------
# Setup subaccount domain (to ensure uniqueness in BTP global account)
# ------------------------------------------------------------------------------------------------------
resource "random_id" "subaccount_domain_suffix" {
  byte_length = 12
}

# ------------------------------------------------------------------------------------------------------
# Creation of subaccount
# ------------------------------------------------------------------------------------------------------
resource "btp_subaccount" "gen_ai" {
  name      = var.subaccount_name
  subdomain = join("-", ["genai-starter-kit", random_id.subaccount_domain_suffix.hex])
  region    = lower(var.region)
}

# ------------------------------------------------------------------------------------------------------
# Prepare & setup the SAP AI Core service (ensure your global account has the respective entitlements)
# ------------------------------------------------------------------------------------------------------
module "ai_setup" {
  source = "./modules/ai"

  subaccount_id             = btp_subaccount.gen_ai.id
  switch_setup_ai_launchpad = var.switch_setup_ai_launchpad
  ai_core_plan_name         = var.ai_core_plan_name
  target_ai_core_model      = var.target_ai_core_model
  admins                    = var.admins

}

module "hana_cloud_setup" {
  source = "./modules/hana-cloud"

  subaccount_id        = btp_subaccount.gen_ai.id
  hana_system_password = var.hana_system_password
  admins               = var.admins
}

resource "local_file" "env_file" {
  content  = join("\n", [module.ai_setup.ai_core_envs, module.hana_cloud_setup.hana_cloud_envs])
  filename = "../../config/secrets/.env"
}
