import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import scraper
import storage
import sys
import requests
import time
import os
from dotenv import load_dotenv
import html

# Load environment variables
load_dotenv()

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Configure logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, 'output', 'scraper_run.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def send_telegram_alert(message):
    """Sends a message to the configured Telegram chat."""
    if not TELEGRAM_TOKEN or "REPLACE_WITH" in TELEGRAM_TOKEN:
        logger.warning("Telegram token not set. Skipping alert.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
             logger.error(f"Telegram send failed: {response.text}")
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

def job():
    """The periodic scraping job."""
    logger.info("Starting scrape job...")
    try:
        activities = scraper.scrape_activity()
        if activities:
            # storage.py now returns the list of NEW items
            new_items = storage.save_new_activities(activities)
            
            if new_items and isinstance(new_items, list):
                logger.info(f"Found {len(new_items)} new items!")
                
                for item in new_items:
                    # Robust HTML formatting with escaping
                    t_type = html.escape(str(item.get('type', 'Unknown')))
                    t_market = html.escape(str(item.get('market_name', 'Unknown')))
                    t_desc = html.escape(str(item.get('description', 'Unknown')))
                    t_time = html.escape(str(item.get('timestamp_str', 'Unknown')))
                    
                    msg = (f"🚨 <b>Activity Detected</b>\n\n"
                           f"<b>Type:</b> {t_type}\n"
                           f"<b>Market:</b> {t_market}\n"
                           f"<b>Info:</b> {t_desc}\n"
                           f"<b>Time:</b> {t_time}")
                    
                    send_telegram_alert(msg)
                    # Sleep briefly to avoid hitting rate limits if many items found
                    time.sleep(0.5)
            else:
                logger.info("No new unique activities found.")
        else:
            logger.info("No activities parsed this run.")
    except Exception as e:
        logger.error(f"Job failed with error: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    
    # Schedule to run every hour (configurable)
    scheduler.add_job(job, 'interval', minutes=60)
    
    logger.info("Scheduler started. Running job every 60 minutes.")
    
    # Run once immediately on startup to verify
    logger.info("Executing initial run...")
    job()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
