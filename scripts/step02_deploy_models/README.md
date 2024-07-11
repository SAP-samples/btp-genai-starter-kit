### Step 2: Deploy AI Models for your genAI experiments in AI Core

That package does the following:

- It loads the content of the `.env` file created in the first step
- It calls the AI Core APIs to give you access to the models you have defined in the file [config/secrets/my_btp_ai_setup.tfvars](config/secrets/my_btp_ai_setup.tfvars) (through the variable `target_ai_core_model`).
