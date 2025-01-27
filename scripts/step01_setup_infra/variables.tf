variable "globalaccount" {
  type        = string
  description = "The globalaccount subdomain where the sub account shall be created."
}

variable "idp" {
  type        = string
  description = "Custom IDP for the BTP account."
  default     = null
}

variable "cli_server_url" {
  type        = string
  description = "The BTP CLI server URL."
  default     = null    #points to default endpoint as maintained in BTP terraform provider
}

variable "switch_setup_ai_launchpad" {
  type        = bool
  description = "Switch to enable the setup of the AI Launchpad."
  default     = true
}

variable "subaccount_name" {
  type        = string
  description = "The subaccount name."
  default     = "My SAP Build Apps subaccount."
}

variable "ai_core_plan_name" {
  type        = string
  description = "The name of the AI Core service plan."
  default     = "extended"
  validation {
    condition     = contains(["extended"], var.ai_core_plan_name)
    error_message = "Valid value(s) for ai_core_plan_name is/are: extended. This is the only service plan allowing access to the generative AI foundation models at this stage."
  }
}

variable "BTP_USERNAME" {
  type        = string
  description = "Your BTP user name (email)."

  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.BTP_USERNAME))
    error_message = "Please enter a valid email address for the BTP_USERNAME."
  }
}

variable "BTP_PASSWORD" {
  type        = string
  description = "Your BTP password."
  sensitive   = true
}

variable "hana_system_password" {
  type        = string
  description = "The password of the database 'superuser' DBADMIN."
  sensitive   = true

  # add validation to check if the password is at least 8 characters long
  validation {
    condition     = length(var.hana_system_password) > 7
    error_message = "The hana_system_password must be at least 8 characters long."
  }

  # add validation to check if the password contains at least one upper case
  validation {
    condition     = can(regex("[A-Z]", var.hana_system_password))
    error_message = "The hana_system_password must contain at least one upper case."
  }

  # add validation to check if the password contains at least two lower case characters that can occur on arbitrary places in the string (not necessarily in a row)
  validation {
    condition     = length(regexall("[a-z]", var.hana_system_password)) > 1
    error_message = "The hana_system_password must contain at least two lower case characters."
  }

  # add validation to check if the password contains at least one numeric character
  validation {
    condition     = can(regex("[0-9]", var.hana_system_password))
    error_message = "The hana_system_password must contain at least one numeric character."
  }
}

variable "target_ai_core_model" {
  type        = list(any)
  description = "Defines the target AI core model to be used by the AI Core service. Depending on the region different foundation models might be available; checkout SAP note 3437766 (https://me.sap.com/notes/3437766) for reference."
  default     = ["gpt-35-turbo"]
}


variable "region" {
  type        = string
  description = "The region where the sub account shall be created in."
  default     = "us10"

  # Checkout https://github.com/SAP-samples/btp-service-metadata/blob/main/v1/developer/aicore.json for the latest list of regions
  # supported by the AI Core service ("extended" plan).
  validation {
    condition     = contains(["ap10", "ap11", "ap20", "ap30", "eu10", "eu11", "eu20", "eu30", "jp10", "sa30", "us10", "us21", "us30"], var.region)
    error_message = "Please enter a valid region for the sub account. Checkout https://github.com/SAP-samples/btp-service-metadata/blob/main/v0/developer/aicore.json for regions providing the AI Core service with the serice plan 'extended'."
  }
}

variable "admins" {
  type        = list(string)
  description = "Defines the colleagues who are added to each subaccount as emergency administrators."

  # add validation to check if admins contains a list of valid email addresses
  validation {
    condition     = length([for email in var.admins : can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", email))]) == length(var.admins)
    error_message = "Please enter a valid email address for the admins."
  }
}
