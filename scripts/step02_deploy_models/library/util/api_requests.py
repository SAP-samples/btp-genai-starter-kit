import requests
import sys
import logging
from library.constants.timings import TIMEOUT_API_CALL, TIME_RETRY_API_CALL
import time

log = logging.getLogger(__name__)


# Function to call a rest API
def call_api(
    type: str, url: str, headers: dict, data: dict = None, message: str = None
):
    timeNeeded = 0
    while timeNeeded < TIMEOUT_API_CALL:
        try:
            r = None
            # Send the request to retrieve the access token
            if type == "POST":
                r = requests.post(url=url, headers=headers, data=data)
            elif type == "GET":
                r = requests.get(url=url, headers=headers)
            # if the response is OK, return the JSON response
            if r.ok is True:
                log.success(f"{message}")
                return r.json()
            else:
                log.info(
                    f"response ({message}): {r.status_code} ({r.reason}): {r.text}"
                )
                log.warning(
                    f"Could not {message}! Re-trying in {TIME_RETRY_API_CALL} seconds..."
                )
                time.sleep(TIME_RETRY_API_CALL)
                timeNeeded += TIME_RETRY_API_CALL
        except requests.exceptions.RequestException as e:
            log.warning(str(e))
            log.error(f"Could not {message}! Exiting...")
            sys.exit(1)
    log.error(f"Could not {message} after {TIMEOUT_API_CALL} seconds! Exiting...")
