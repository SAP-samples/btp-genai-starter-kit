# ------------------------------------------------------------------------------------------------------
# Provider configuration
# ------------------------------------------------------------------------------------------------------
# Your global account subdomain
globalaccount = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Custom IDP for the BTP account. By defauilt, it is set to point to BTP CLI server on the Live BTP landscape. Only change this if you use custom IDP for SAP BTP platform users.
#idp = "<your-trusted-idp-name>"

# Region for your subaccount
region        = "us10"

# Name and technical domain of your sub account
subaccount_name = "GenAI starter-kit experiments"
admins  = ["jane.doe@test.com", "john.doe@test.com"]

# If set to true, the script will create an app subdomain for the AI Launchpad
switch_setup_ai_launchpad = false

# The model that the AI Core service should use
target_ai_core_model = ["gpt-35-turbo", "text-embedding-ada-002"]

# Comment out the next line if you want to provide the password here instead of typing it in the console (not recommended for security reasons)
# Make sure you respect the minimum requirements: len>=8 chars, 1+ upper case char, 2+ lower-case char, 1+ digit
# hana_system_password = "" 