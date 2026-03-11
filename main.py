import logging
import logging.handlers
import os

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log", 
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

try:
    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER")
    
except KeyError:
    logger.info("PUSHOVER_TOKEN not available!")
    logger.info("PUSHOVER_USER not available!")
    raise

if __name__ == "__main__":
    r = requests.post("https://api.pushover.net/1/messages.json", data={
        "token": token,
        "user": user,
        "message": "Congratulations! you got the winning combinations!",
        "title": "You won the lotto last tonight!",
        "url": "https://www.pcso.gov.ph/searchlottoresult.aspx",
        "url_title": "View Lotto Results!",
        "priority": 1
    })

    if r.status_code == 200:
        data = r.json()
        logger.info(f'The status code was {r.status_code}')