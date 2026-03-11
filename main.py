import logging
import logging.handlers
import os
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Logging Setup ---
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

def send_notification(token, user, title, message):
    r = requests.post("https://api.pushover.net/1/messages.json", data={
        "token": token,
        "user": user,
        "message": message,
        "title": title,
        "url": "https://www.pcso.gov.ph/searchlottoresult.aspx",
        "url_title": "View Lotto Results!",
        "priority": 1
    })
    logger.info(f"Pushover sent. Status: {r.status_code}")

if __name__ == "__main__":
    # Load Credentials
    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER")

    if not token or not user:
        logger.error("Missing PUSHOVER_TOKEN or PUSHOVER_USER environment variables!")
        exit(1)

    # --- Selenium Setup ---
    chrome_options = Options()
    options = [
        "--headless",
        "--disable-gpu",
        "--window-size=1920,1200",
        "--ignore-certificate-errors",
        "--disable-extensions",
        "--no-sandbox",
        "--disable-dev-shm-usage"
    ]
    for option in options:
        chrome_options.add_argument(option)

    # Use Chromium for better compatibility with GitHub Actions runners
    # service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        logger.info("Accessing PCSO/Target Website...")
        driver.get('https://www.pcso.gov.ph/searchlottoresult.aspx')
        
        # Log the title to verify access
        page_title = driver.title
        logger.info(f"Successfully accessed page. Title: {page_title}")

        # YOUR LOGIC HERE: 
        # e.g., if "Jackpot" in driver.page_source:
        
        # Testing notification
        send_notification(token, user, "PCSO Checker Active", f"Accessed: {page_title}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
        logger.info("Driver closed.")