
terraform {
  required_providers {
    btp = {
      source  = "SAP/btp"
      version = "~> 1.3.0"
    }
  }
}

provider "btp" {
  globalaccount  = var.globalaccount
  password       = var.BTP_PASSWORD
  username       = var.BTP_USERNAME
}
