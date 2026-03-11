import logging
import logging.handlers
import os
import requests
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        "url": "https://www.lottopcso.com/lotto-result-today-summary/",
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
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        logger.info("Accessing PCSO/Target Website...")
        driver.get('https://www.lottopcso.com/6-45-lotto-result/')
        
        # Log the title to verify access
        page_title = driver.title
        logger.info(f"Successfully accessed page. Title: {page_title}")

        # 1. Wait for the table to actually load (important for Selenium)
        wait = WebDriverWait(driver, 10)
        
        # 2. Define the XPath to Row 1, Column 2
        # Note: If the first row is a header, it might be <th> instead of <td>
        xpath_target = "/html/body/div[2]/div/div/article/div[2]/figure[1]/table/tbody/tr[1]/td[2]"
        
        # 3. Find the element and get text
        winning_numbers_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath_target)))
        winning_text = winning_numbers_element.text
        
        logger.info(f"Extracted Text from Row 1, Col 2: {winning_text}")
        print(f"Result: {winning_text}") 

        if winning_text:
            send_notification(token, user, "Latest 6/45 Result", f"The winning numbers are: {winning_text}")
        
        # Testing notification
        send_notification(token, user, "PCSO Checker Active", f"Accessed: {page_title}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
        logger.info("Driver closed.")