import os


def get_script_dir(executable: str = None):
    """
    Returns the directory path of the current script.

    Returns:
        str: The absolute path of the directory containing the script.
    """
    return os.path.dirname(
        os.path.abspath(executable if executable is not None else __file__)
    )
