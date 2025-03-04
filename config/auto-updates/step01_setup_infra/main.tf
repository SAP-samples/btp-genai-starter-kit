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

# Assign Role Collection(Subaccount Administrator) to users
resource "btp_subaccount_role_collection_assignment" "subaccount_admin" {
  for_each             = toset([for admin in var.admins: admin if admin != var.BTP_USERNAME])
  subaccount_id        = btp_subaccount.gen_ai.id
  role_collection_name = "Subaccount Administrator"
  user_name            = each.value
}

# ------------------------------------------------------------------------------------------------------
# Prepare & setup the SAP AI Core service (ensure your global account has the respective entitlements)
# ------------------------------------------------------------------------------------------------------
module "ai_setup" {
  source = "./modules/ai"

  subaccount_id             = btp_subaccount.gen_ai.id
  ai_core_plan_name         = var.ai_core_plan_name
  admins                    = var.admins

}


resource "local_file" "env_file" {
  content  = join("\n", [module.ai_setup.ai_core_envs])
  filename = "../../secrets/auto-update.env"
}
