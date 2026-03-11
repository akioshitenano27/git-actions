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

from dotenv import load_dotenv

from datetime import datetime

# .strftime("%H:%M:%S") formats it to 24-hour time
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logging.info(f"Current Server Time: {now}")

# This looks for a .env file and loads the variables into os.environ
load_dotenv()

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

def check_lotto_results(player_pick, winning_numbers):
    # Convert strings "05-11-..." into sets of integers {5, 11, ...}
    player_set = set(player_pick.split('-'))
    winning_set = set(winning_numbers.split('-'))
    
    # Find the intersection (numbers that appear in both sets)
    matches = player_set.intersection(winning_set)
    match_count = len(matches)
    
    # PCSO Prize Logic
    result_message = ""
    is_win = False
    
    if match_count == 6:
        result_message = "JACKPOT!! You hit all 6 numbers!"
        is_win = True
    elif match_count == 5:
        result_message = "2nd Prize! You matched 5 numbers!"
        is_win = True
    elif match_count == 4:
        result_message = "3rd Prize! You matched 4 numbers!"
        is_win = True
    elif match_count == 3:
        result_message = "You won 3rd prize (standard) consolation prize!"
        is_win = True
    elif match_count == 2:
        result_message = "We atleast matched 2 numbers! Try your luck today!"
        is_win = False
    elif match_count == 1:
        result_message = "We atleast matched 1 numbers! Try your luck today!"
        is_win = False
    else:
        result_message = f"Your luck is about to come!"
        is_win = False
        
    return match_count, result_message, is_win

def process_lotto_game(driver, game_config, token, user):
    """Processes a single lotto game type."""
    game_name = game_config['name']
    url = game_config['url']
    env_prefix = game_config['env_prefix']
    
    # Dynamically grab all env vars that start with the prefix (e.g., SIX_FIFTY_EIGHT_1, _2, etc.)
    user_tickets = [os.getenv(key) for key in os.environ if key.startswith(env_prefix)]
    user_tickets = [t for t in user_tickets if t] # filter out None

    if not user_tickets:
        logging.info(f"No tickets found for {game_name} (Prefix: {env_prefix}). Skipping.")
        return

    try:
        logging.info(f"Accessing {game_name} results...")
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        
        # Your XPaths (reused for all games)
        num_xpath = "/html/body/div[2]/div/div/article/div[2]/figure[1]/table/tbody/tr[1]/td[2]"
        winning_text = wait.until(EC.presence_of_element_located((By.XPATH, num_xpath))).text
        
        logging.info(f"{game_name} Winning Numbers: {winning_text}")

        # Check each ticket for this game
        for ticket in user_tickets:
            match_count, result_message, is_win = check_lotto_results(ticket, winning_text)
            
            status = "WINNER!" if is_win else "Result"
            message = f"{game_name} {status}\n\nWinning: {winning_text}\nYour Numbers: {ticket}\n{result_message}"
            
            send_notification(token, user, f"Latest {game_name} Result", message)
            time.sleep(3)

    except Exception as e:
        logging.error(f"Error processing {game_name}: {str(e)}")

if __name__ == "__main__":
    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER")

    if not token or not user:
        exit(1)

    # Define your game mappings
    LOTTO_GAMES = [
        {"name": "6/58", "url": "https://www.lottopcso.com/6-58-lotto-result/", "env_prefix": "SIX_FIFTY_EIGHT_"},
        {"name": "6/55", "url": "https://www.lottopcso.com/6-55-lotto-result/", "env_prefix": "SIX_FIFTY_FIVE_"},
        {"name": "6/49", "url": "https://www.lottopcso.com/6-49-lotto-result/", "env_prefix": "SIX_FORTY_NINE_"},
        {"name": "6/45", "url": "https://www.lottopcso.com/6-45-lotto-result/", "env_prefix": "SIX_FORTY_FIVE_"},
    ]

    # Selenium Setup (Headless)
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

    for opt in options:
        chrome_options.add_argument(opt)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        for game in LOTTO_GAMES:
            process_lotto_game(driver, game, token, user)

    # except Exception as e:
        # logger.error(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
        logger.info("Driver closed.")