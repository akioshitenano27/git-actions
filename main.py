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
    SOME_SECRET = os.environ["SOME_SECRET"]
except KeyError:
    SOME_SECRET = "Token not available!"
    #logger.info("Token not available!")
    #raise


if __name__ == "__main__":
    logger.info(f"Token value: {SOME_SECRET}")
    # Get secrets from Environment Variables
    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER")

    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": token,
        "user": user,
        "message": "Congratulations! you got the winning combinations!",
        "title": "You won the lotto last tonight!",
        "url": "https://www.pcso.gov.ph/searchlottoresult.aspx",
        "url_title": "View Lotto Results!",
        "priority": 1
    })


    r = requests.get('https://weather.talkpython.fm/api/weather/?city=Berlin&country=DE')
    if r.status_code == 200:
        data = r.json()
        temperature = data["forecast"]["temp"]
        logger.info(f'Weather in Berlin: {temperature}')