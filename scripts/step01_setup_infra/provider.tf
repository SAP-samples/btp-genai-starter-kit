
terraform {
  required_providers {
    btp = {
      source  = "SAP/btp"
      version = "~> 1.2.0"
    }
  }
}

provider "btp" {
  globalaccount  = var.globalaccount
  cli_server_url = var.cli_server_url
  password       = var.BTP_PASSWORD
  username       = var.BTP_USERNAME
}
