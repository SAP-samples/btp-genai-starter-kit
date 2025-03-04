from dataclasses import dataclass
from json import JSONEncoder


class AiCoreMetadataJsonEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


@dataclass
class AiCoreMetadata:
    authUrl: str
    clientId: str
    clientSecret: str
    resourceGroup: str
    apiBase: str
    resourceGroup: str
    targetAiCoreModel: str
    apiAccessToken: str
    availableModels: str
    configurationIds: list
    deployments: list
    show_http_debug: bool = False

    def __getitem__(self, item):
        return getattr(self, item)
