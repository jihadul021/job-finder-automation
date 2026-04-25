import logging
import json
from datetime import datetime
from scraper import fetch_jobs
from filter import filter_jobs
from scorer import score_jobs
from storage import save_to_sheets

# Set up logging to both terminal and a log file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("job_automation.log"),
        logging.StreamHandler()
    ]
)

def load_config():
    """Load config from config.json"""
    with open("config.json", "r") as f:
        return json.load(f)

def print_summary(all_jobs, filtered_jobs, scored_jobs, new_added):
    """Print a clean summary at the end of each run"""
    print("\n" + "="*50)
    print("   JOB AUTOMATION — RUN SUMMARY")
    print("="*50)
    print(f"  Run time        : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Total fetched   : {len(all_jobs)}")
    print(f"  After filtering : {len(filtered_jobs)}")
    print(f"  New jobs added  : {new_added}")
    print("="*50)
    print("\n  TOP 5 JOBS THIS RUN:")
    print("-"*50)
    for i, job in enumerate(scored_jobs[:5], 1):
        print(f"  {i}. [{job['score']}pts] {job['title']}")
        print(f"     {job['company']} — {job['location']}")
        print(f"     {job['link'][:60]}...")
        print()
    print("="*50)
    print("  Check your Google Sheet for full results!")
    print("="*50 + "\n")

def run():
    """
    Main pipeline:
    fetch → filter → score → save → summarize
    """
    logging.info("="*40)
    logging.info("Job Automation Run Started")
    logging.info("="*40)

    config = load_config()

    # Step 1: Fetch raw jobs from API
    logging.info("STEP 1: Fetching jobs...")
    all_jobs = fetch_jobs()

    if not all_jobs:
        logging.error("No jobs fetched. Check your API key or internet connection.")
        return

    # Step 2: Filter relevant jobs
    logging.info("STEP 2: Filtering jobs...")
    filtered_jobs = filter_jobs(all_jobs, config)

    if not filtered_jobs:
        logging.warning("No relevant jobs found after filtering. Try broadening your config keywords.")
        return

    # Step 3: Score and rank jobs
    logging.info("STEP 3: Scoring jobs...")
    scored_jobs = score_jobs(filtered_jobs, config)

    # Step 4: Save to Google Sheets
    logging.info("STEP 4: Saving to Google Sheets...")
    new_added = save_to_sheets(scored_jobs)

    # Step 5: Print summary
    print_summary(all_jobs, filtered_jobs, scored_jobs, new_added)

    logging.info("Run completed successfully!")

if __name__ == "__main__":
    run()