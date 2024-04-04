
output "hana_cloud_service_instance_id" {
  value       = btp_subaccount_service_instance.hana_cloud.id
  description = "The ID of the HANA Cloud service instance."
}

output "hana_cloud_service_instance_name" {
  value       = btp_subaccount_service_instance.hana_cloud.name
  description = "The ID of the HANA Cloud service instance."
}

output "hana_cloud_envs"{
  value = <<-EOT
  HANA_DB_ADDRESS=${jsondecode(btp_subaccount_service_binding.hana_cloud.credentials)["host"]}
  HANA_DB_PORT=${jsondecode(btp_subaccount_service_binding.hana_cloud.credentials)["port"]}
  HANA_DB_USER=DBADMIN
  HANA_DB_PASSWORD=${var.hana_system_password}
  EOT
  description = "Environment variables for the HANA Cloud service."
}