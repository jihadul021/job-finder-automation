import schedule
import time
import logging
from main import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("job_automation.log"),
        logging.StreamHandler()
    ]
)

def start_scheduler():
    """
    Schedule the job automation to run automatically.
    Runs every day at 9:00 AM.
    """
    logging.info("Scheduler started — job automation will run daily at 09:00")

    # Run once immediately on startup
    logging.info("Running immediately on startup...")
    run()

    # Then schedule daily at 9am
    schedule.every().day.at("09:00").do(run)

    logging.info("Next run scheduled for 09:00 tomorrow. Waiting...")

    # Keep the script alive — checks every minute if it's time to run
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start_scheduler()