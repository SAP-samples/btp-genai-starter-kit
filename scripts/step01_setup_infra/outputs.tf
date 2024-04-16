output "globalaccount_id" {
  value       = var.globalaccount
    description = "The ID of the global account."
}

output "subaccount_id" {
  value       = btp_subaccount.gen_ai.id
  description = "The ID of the project subaccount."
}

output "subaccount_name" {
  value       = var.subaccount_name
  description = "The name of the project subaccount."
}

output "subaccount_region" {
  value       = var.region
  description = "The ID of the project subaccount."
}

output "ai_core_service_instance_id" {
  value       = module.ai_setup.ai_core_service_instance_id
  description = "The ID of the AI Core service instance."
}

output "ai_core_service_instance_name" {
  value       = module.ai_setup.ai_core_service_instance_name
  description = "The ID of the AI Core service instance."
}

output "hana_cloud_service_instance_id" {
  value       = module.hana_cloud_setup.hana_cloud_service_instance_id
  description = "The ID of the HANA Cloud service instance."
}

output "hana_cloud_service_instance_name" {
  value       = module.hana_cloud_setup.hana_cloud_service_instance_name
  description = "The ID of the HANA Cloud service instance."
}

output "timestamp_test_finished"{
    value = timestamp()
    description = "The current time"
}
