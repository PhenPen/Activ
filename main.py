import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import scraper
import storage
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_run.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def job():
    """The periodic scraping job."""
    logger.info("Starting scrape job...")
    try:
        activities = scraper.scrape_activity()
        if activities:
            logger.info(f"Scraped {len(activities)} items.")
            count = storage.save_new_activities(activities)
            logger.info(f"Successfully saved {count} new unique activities.")
        else:
            logger.info("No activities found or scrape failed.")
    except Exception as e:
        logger.error(f"Job failed with error: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    
    # Schedule to run every hour (configurable)
    # For testing purposes, you might want to change this to minutes=1
    scheduler.add_job(job, 'interval', minutes=60)
    
    logger.info("Scheduler started. Running job every 60 minutes.")
    
    # Run once immediately on startup to verify
    logger.info("Executing initial run...")
    job()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
