from dotenv import load_dotenv
import os   
load_dotenv()
import requests
import json
import logging
import time


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_config():
    """Load config from config.json and secrets from .env"""
    with open("config.json", "r") as f:
        config = json.load(f)

    # Load secrets from .env instead of config.json
    config["rapidapi_key"] = os.getenv("RAPIDAPI_KEY")
    config["adzuna_app_id"] = os.getenv("ADZUNA_APP_ID")
    config["adzuna_app_key"] = os.getenv("ADZUNA_APP_KEY")
    config["sheet_id"] = os.getenv("SHEET_ID")

    return config

def fetch_jobs():
    """
    Fetch job listings from JSearch API based on config preferences.
    Returns a list of job dictionaries.
    """
    config = load_config()
    all_jobs = []

    for role in config["roles"]:
        logging.info(f"Searching jobs for: {role}")

        query = f"{role} {config['location']}"
        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": config["rapidapi_key"],
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

        for page in range(1, config["num_pages"] + 1):
            params = {
                "query": query,
                "page": str(page),
                "num_pages": "1",
                "date_posted": config["date_posted"],
                "remote_jobs_only": "true",
            }

            try:
                response = requests.get(url, headers=headers, params=params, timeout=15)
                response.raise_for_status()

                data = response.json()
                jobs = data.get("data", [])
                logging.info(f"  Page {page}: found {len(jobs)} jobs")

                for job in jobs:
                    all_jobs.append({
                        "title": job.get("job_title", "N/A"),
                        "company": job.get("employer_name", "N/A"),
                        "location": job.get("job_city", "") or "Remote",
                        "description": job.get("job_description", ""),
                        "link": job.get("job_apply_link", "N/A"),
                        "posted_date": job.get("job_posted_at_datetime_utc", "N/A"),
                        "source": job.get("job_publisher", "N/A"),
                        "salary_min": job.get("job_min_salary", "N/A"),
                        "salary_max": job.get("job_max_salary", "N/A"),
                        "country": job.get("job_country", "N/A"),
                    })

                # Wait 2 seconds between requests to avoid rate limiting
                time.sleep(2)

            except requests.exceptions.Timeout:
                logging.error(f"  Timeout on page {page} for role: {role}")
            except requests.exceptions.RequestException as e:
                logging.error(f"  Request failed: {e}")
                # If rate limited, wait longer and retry
                if "429" in str(e):
                    logging.info("  Rate limited — waiting 10 seconds...")
                    time.sleep(10)

    logging.info(f"Total raw jobs fetched: {len(all_jobs)}")
    return all_jobs