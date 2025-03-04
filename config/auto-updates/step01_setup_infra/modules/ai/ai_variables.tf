variable "subaccount_id" {
  type        = string
  description = "The subaccount domain (has to be unique within the BTP region)."
}

variable "ai_core_plan_name" {
  type        = string
  description = "The name of the AI Core service plan."
  default     = "extended"
  validation {
    condition     = contains(["sap-internal", "extended"], var.ai_core_plan_name)
    error_message = "Valid values for ai_core_plan_name are: sap-internal, extended."
  }
}

variable "target_ai_core_model" {
  type        = list(any)
  description = "Defines the target AI core model to be used by the AI Core service"
  default     = ["gpt-35-turbo"]

  validation {
    condition = length([
      for o in var.target_ai_core_model : true
      if contains([
        "tiiuae--falcon-40b-instruct",
        "mistralai--mixtral-8x7b-instruct-v01",
        "meta--llama3-70b-instruct",
        "anthropic--claude-3-sonnet",
        "anthropic--claude-3-haiku",
        "anthropic--claude-3-opus",
        "amazon--titan-embed-text",
        "amazon--titan-text-lite",
        "amazon--titan-text-express",
        "gpt-35-turbo",
        "gpt-35-turbo-16k",
        "gpt-4",
        "gpt-4-32k",
        "text-embedding-ada-002",
        "text-embedding-3-small",
        "text-embedding-3-large",
        "gpt-4o",
        "text-bison",
        "chat-bison",
        "textembedding-gecko",
        "textembedding-gecko-multilingual",
        "gemini-1.0-pro",
      ], o)
    ]) == length(var.target_ai_core_model)
    error_message = "Please enter a valid entry for the target_ai_core_model of the AI Core service. See https://help.sap.com/docs/sap-ai-core/sap-ai-core-service-guide/models-and-scenarios-in-generative-ai-hub (Model Name) for the list of supported values."  
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

variable "switch_setup_ai_launchpad" {
  type        = bool
  description = "Switch to enable the setup of the AI Launchpad."
  default     = false
}

# Define roles for a user of the SAP AI Launchpad
variable "roles_ai_launchpad" {
  type        = list(string)
  description = "Defines the list of roles to be assigned to the users in the AI Launchpad."
  default = [
    "ailaunchpad_aicore_admin_editor",
    "ailaunchpad_allow_all_resourcegroups",
    "ailaunchpad_genai_administrator",
    "ailaunchpad_mloperations_editor",
    "ailaunchpad_connections_editor"
  ]

}
