
variable "subaccount_id" {
  type        = string
  description = "The subaccount id."
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

variable "admins" {
  type        = list(string)
  description = "Defines the colleagues who are added to each subaccount as emergency administrators."

  # add validation to check if admins contains a list of valid email addresses
  validation {
    condition     = length([for email in var.admins : can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", email))]) == length(var.admins)
    error_message = "Please enter a valid email address for the admins."
  }

}
