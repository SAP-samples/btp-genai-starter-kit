from pathlib import Path

# Folders
ROOT = Path(__file__, "..", "..", "..", "..", "..", "..").resolve()
FOLDER_SECRETS = Path(ROOT, "config", "secrets")
print(ROOT)

# Files
FILE_METADATA_AI_CORE_KEY = Path(
    FOLDER_SECRETS, "my_metadata_ai_core_key.json"
).resolve()
FILE_ENV = Path(FOLDER_SECRETS, "auto-update.env").resolve()

FILE_TERRAFORM_VARIABLE_AVAILABLE_MODELS = Path(
    ROOT,
    "scripts",
    "step01_setup_infra",
    "modules",
    "ai",
    "ai_variable_target_ai_core_model.tf",
)
