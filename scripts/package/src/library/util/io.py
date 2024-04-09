from pathlib import Path
import logging
import json

log = logging.getLogger(__name__)


# Read file and return content
def read_file(file_path: Path):
    try:
        with open(file_path, "r") as file:
            filedata = file.read()
        return filedata
    except IOError:
        log.warning("Can't open file >" + str(file_path) + "<")
        return None


# Get json file content
def read_json_file(file_path):
    try:
        # Opening JSON file
        f = open(file_path)
        # returns JSON object as a dictionary
        data = json.load(f)
        return data
    except IOError:
        log.warning("Can't open json file >" + str(file_path) + "<")
        return None


# Write variable content to file
def write_file(file_path, content):
    try:
        f = open(file_path, "w")
        f.write(content)
        f.close()
        log.info("File written >" + str(file_path) + "<")
    except IOError:
        log.warning("Can't write to file >" + str(file_path) + "<")
        return None


# function to fetch all files in a folder with a glob pattern recursively
def get_files_in_folder(folder, glob_pattern):
    files = []
    for path in Path(folder).rglob(glob_pattern):
        files.append(path)
    return files
