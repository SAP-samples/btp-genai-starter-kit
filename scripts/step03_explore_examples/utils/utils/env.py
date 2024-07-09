import os
from dotenv import load_dotenv
from pathlib import Path


def _load_env_from_root(verbose: bool = False):
    root_path = Path(__file__).resolve().parent.parent.parent.parent.parent

    folder_to_secrets = Path(root_path, "config", "secrets")
    path_to_env = _search_env_file(folder_to_secrets)
    if path_to_env is None:
        raise FileNotFoundError("Environment file not found in config/secrets.")

    if verbose is True:
        print(f"Loading environment variables from {path_to_env}")

    return path_to_env


def _search_env_file(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file == ".env":
                return Path(root, file).resolve()
    return None


def init_env(
    from_project_root: bool = True,
    mandatory_env_variables: list = [
        "AICORE_AUTH_URL",
        "AICORE_CLIENT_ID",
        "AICORE_CLIENT_SECRET",
        "AICORE_BASE_URL",
        "AICORE_RESOURCE_GROUP",
        "HANA_DB_ADDRESS",
        "HANA_DB_PORT",
        "HANA_DB_USER",
        "HANA_DB_PASSWORD",
    ],
    verbose: bool = False,
):
    """
    Initializes the environment by loading environment variables from a .env file.

    Args:
        from_project_root (bool, optional): Specifies whether to load the .env file from the project root directory.
                                            Defaults to False.
        mandatory_env_variables (list, optional): A list of environment variables that are required to be present.
                                                  Defaults to an empty list.

    Raises:
        Exception: If an error occurs while loading the environment variables.

    """
    try:
        if from_project_root is True:
            file_env = _load_env_from_root()
            load_dotenv(dotenv_path=file_env, verbose=True)
        else:
            load_dotenv(verbose=True)

        assert_env(mandatory_env_variables, verbose=verbose)
    except Exception as e:
        print(f"An error occurred while loading environment variables: {str(e)}")


def check_env_variable(env_variable: str, verbose: bool = False):
    """
    Checks if the specified environment variable is set.

    Args:
            env_variable (str): The name of the environment variable to check.

    Raises:
            ValueError: If the environment variable is not set.

    """
    if env_variable not in os.environ:
        raise ValueError(f"Environment variable {env_variable} is not set.")

    if verbose is True:
        print(f"Environment variable {env_variable} is set.")


def assert_env(env_variables: list, verbose: bool = False):
    """
    Asserts that the specified environment variables are set.

    Args:
            env_variables (list): A list of environment variable names to check.

    Raises:
            ValueError: If any of the specified environment variables are not set.

    Returns:
            None
    """

    for env_variable in env_variables:
        check_env_variable(env_variable, verbose=verbose)
