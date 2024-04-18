from dataclasses import dataclass
from library.model.aicore import AiCoreMetadata as AiCoreMetadataDefinition
import os
import logging
import json
import time
import base64
import sys
from library.constants.timings import TIMEOUT_API_CALL, TIME_RETRY_API_CALL
from library.util.api_requests import call_api

log = logging.getLogger(__name__)


@dataclass
class AiCoreMetadata(AiCoreMetadataDefinition):
    def __init__(self):
        self.authUrl = os.environ.get("AICORE_AUTH_URL")
        self.clientId = os.environ.get("AICORE_CLIENT_ID")
        self.clientSecret = os.environ.get("AICORE_CLIENT_SECRET")
        self.resourceGroup = os.environ.get("AICORE_RESOURCE_GROUP")
        self.apiBase = os.environ.get("AICORE_BASE_URL")
        self.targetAiCoreModel = json.loads(os.environ.get("TARGET_AI_CORE_MODEL"))
        self.apiAccessToken = get_api_access_token(self)
        self.availableModels = get_available_ai_models(self)
        self.configurationIds = create_configuration(self)
        self.deployment = create_deployments(self)


# Retrieve the access token from the AI Core system
def get_api_access_token(aiCoreMetadata: AiCoreMetadataDefinition) -> str:
    clientId = aiCoreMetadata.clientId
    clientSecret = aiCoreMetadata.clientSecret
    authUrl = aiCoreMetadata.authUrl

    # Create the authorization string
    authorizationString = f"{clientId}:{clientSecret}"
    # Encode the authorization string
    byte_data = authorizationString.encode("utf-8")
    # Base64 encode the byte data
    clientSecretBase64 = base64.b64encode(byte_data).decode("utf-8")

    # Create the URL to retrieve the access token
    aiCoreLocation = f"{authUrl}/oauth/token?grant_type=client_credentials"
    # Create the headers for the request
    headers = {"Authorization": f"Basic {clientSecretBase64}"}

    response = call_api(
        "POST",
        aiCoreLocation,
        headers,
        None,
        "retrieve access token from AI Core system",
    )

    return response["access_token"]


# Retrieve the available AI models from the AI Core system
def get_available_ai_models(aiCoreMetadata: AiCoreMetadataDefinition) -> str:
    token = aiCoreMetadata.apiAccessToken
    apiBase = aiCoreMetadata.apiBase

    # Create the URL to retrieve the available AI models
    aiCoreLocation = f"{apiBase}/v2/lm/scenarios/foundation-models/executables"
    # Create the headers for the request
    headers = {
        "AI-Resource-Group": aiCoreMetadata.resourceGroup,
        "Authorization": f"Bearer {token}",
    }

    response = call_api(
        "GET",
        aiCoreLocation,
        headers,
        None,
        "retrieve available AI models from AI Core system",
    )

    return response


# Create the configurations for the AI models in the AI Core system
def create_configuration(aiCoreMetadata: AiCoreMetadataDefinition) -> str:
    apiBase = aiCoreMetadata.apiBase
    token = aiCoreMetadata.apiAccessToken
    resourceGroup = aiCoreMetadata.resourceGroup

    configurationIDs = []

    # Create the URL to create the configuration
    aiCoreLocation = f"{apiBase}/v2/lm/configurations"
    # Create the headers for the request
    headers = {}
    headers["AI-Resource-Group"] = resourceGroup
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {token}"

    if (
        aiCoreMetadata.availableModels is None
        or aiCoreMetadata.availableModels.get("resources") is None
        or len(aiCoreMetadata.availableModels["resources"]) == 0
    ):
        log.error("No available resources found! with available models. Exiting...")
        sys.exit(1)

    # Loop through the available models and find the one that matches the target model
    for model in aiCoreMetadata.availableModels["resources"]:
        for parameter in model["parameters"]:
            supportedModels = get_supported_models(parameter)
            for targetAiCoreModel in aiCoreMetadata.targetAiCoreModel:
                if targetAiCoreModel in supportedModels:
                    data = {}
                    data["name"] = targetAiCoreModel + "-config"
                    data["executableId"] = model["id"]
                    data["scenarioId"] = model["scenarioId"]
                    data["versionId"] = model["versionId"]
                    data["parameterBindings"] = []
                    data["parameterBindings"].append(
                        {"key": "modelName", "value": targetAiCoreModel}
                    )

                    response = call_api(
                        "POST",
                        aiCoreLocation,
                        headers,
                        json.dumps(data),
                        f"create configuration for AI Core model {targetAiCoreModel}",
                    )
                    configuration = response
                    configurationIDs.append(configuration["id"])

    return configurationIDs


# Create the deployments for the AI models in the AI Core system
def create_deployments(aiCoreMetadata: AiCoreMetadataDefinition) -> list:
    final_deployments = []

    apiBase = aiCoreMetadata.apiBase
    token = aiCoreMetadata.apiAccessToken
    resourceGroup = aiCoreMetadata.resourceGroup

    # Create the URL to create the configuration
    aiCoreLocation = f"{apiBase}/v2/lm/deployments"
    # Create the headers for the request
    headers = {}
    headers["AI-Resource-Group"] = resourceGroup
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {token}"

    deploymentIds = []

    for configurationId in aiCoreMetadata.configurationIds:
        data = {}

        data["configurationId"] = configurationId
        response = call_api(
            "POST",
            aiCoreLocation,
            headers,
            json.dumps(data),
            f"deploy AI Core model for configuration id {configurationId}",
        )
        deploymentIds.append(response["id"])

    for deploymenId in deploymentIds:
        deploymentDetails = get_deployment_details(aiCoreMetadata, deploymenId)
        final_deployments.append(deploymentDetails)

    return final_deployments


# Retrieve the deployment details from the AI Core system metadata
def get_deployment_details(aiCoreMetadata: AiCoreMetadataDefinition, deploymenId: str):
    apiBase = aiCoreMetadata.apiBase
    token = aiCoreMetadata.apiAccessToken
    resourceGroup = aiCoreMetadata.resourceGroup

    # Create the URL to create the configuration
    aiCoreLocation = f"{apiBase}/v2/lm/deployments/{deploymenId}"
    # Create the headers for the request
    headers = {}
    headers["AI-Resource-Group"] = resourceGroup
    headers["Authorization"] = f"Bearer {token}"
    deploymentDetails = None

    timeNeeded = 0
    message = f"retrieve deployment details for deployment id {deploymenId}"
    while timeNeeded < TIMEOUT_API_CALL:
        # Send the request to create the deployment
        response = call_api("GET", aiCoreLocation, headers, None, message)

        deploymentDetails = response
        deploymentUrl = deploymentDetails["deploymentUrl"]
        if deploymentUrl != "":
            log.success(f"AI Core deployment id '{deploymenId}' is now accessible!")
            return deploymentDetails
        else:
            log.warning(
                f"Could not {message} (deployment not finished)! Re-trying in {TIME_RETRY_API_CALL} seconds..."
            )

            time.sleep(TIME_RETRY_API_CALL)
            timeNeeded += TIME_RETRY_API_CALL

    log.error(
        f"Could not retrieve deployment details for id '{deploymenId}'! Exiting..."
    )
    sys.exit(1)


# Extract the supported models from the parameters description
def get_supported_models(parameters: dict) -> list[str]:
    result = []

    if parameters.get("description") is not None:
        split = parameters["description"].split("supportedModels: ")
        if len(split) > 1:
            result = split[1].split(", ")

    return result
