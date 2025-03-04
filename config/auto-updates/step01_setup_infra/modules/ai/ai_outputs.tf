output "ai_core_service_instance_id" {
  value       = btp_subaccount_service_instance.ai_core.id
  description = "The ID of the AI Core service instance."
}

output "ai_core_service_instance_name" {
  value       = btp_subaccount_service_instance.ai_core.name
  description = "The ID of the AI Core service instance."
}

output "ai_core_envs" {
  value       = <<-EOT
  AICORE_AUTH_URL=${jsondecode(btp_subaccount_service_binding.ai_core_binding.credentials)["url"]}
  AICORE_CLIENT_ID=${jsondecode(btp_subaccount_service_binding.ai_core_binding.credentials)["clientid"]}
  AICORE_CLIENT_SECRET=${jsondecode(btp_subaccount_service_binding.ai_core_binding.credentials)["clientsecret"]}
  AICORE_BASE_URL=${jsondecode(btp_subaccount_service_binding.ai_core_binding.credentials)["serviceurls"]["AI_API_URL"]}
  AICORE_RESOURCE_GROUP=default
  EOT
  description = "The environment variables for the AI Core service."
}