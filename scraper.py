import requests
import json
import logging
import time
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_config():
    """Load config from config.json and secrets from .env"""
    with open("config.json", "r") as f:
        config = json.load(f)

    config["rapidapi_key"] = os.getenv("RAPIDAPI_KEY")
    config["adzuna_app_id"] = os.getenv("ADZUNA_APP_ID")
    config["adzuna_app_key"] = os.getenv("ADZUNA_APP_KEY")
    config["sheet_id"] = os.getenv("SHEET_ID")

    return config


def fetch_jsearch_jobs(config):
    """
    Fetch jobs from JSearch API (LinkedIn, Indeed, Glassdoor).
    """
    all_jobs = []

    for role in config["roles"]:
        logging.info(f"[JSearch] Searching: {role}")

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
                        "source": "JSearch",
                        "salary_min": job.get("job_min_salary", "N/A"),
                        "salary_max": job.get("job_max_salary", "N/A"),
                        "country": job.get("job_country", "N/A"),
                    })

                time.sleep(2)

            except requests.exceptions.Timeout:
                logging.error(f"  Timeout on page {page} for role: {role}")
            except requests.exceptions.RequestException as e:
                logging.error(f"  Request failed: {e}")
                if "429" in str(e):
                    logging.info("  Rate limited — waiting 10 seconds...")
                    time.sleep(10)

    logging.info(f"[JSearch] Total jobs fetched: {len(all_jobs)}")
    return all_jobs


def fetch_adzuna_jobs(config):
    """
    Fetch jobs from Adzuna API — free, official, global job board.
    US only for remote junior/intern roles.
    """
    all_jobs = []

    for role in config["roles"]:
        logging.info(f"[Adzuna] Searching: {role}")

        url = "https://api.adzuna.com/v1/api/jobs/us/search/1"

        params = {
            "app_id": config["adzuna_app_id"],
            "app_key": config["adzuna_app_key"],
            "results_per_page": 20,
            "what": f"{role} remote",
            "content-type": "application/json",
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            jobs = data.get("results", [])
            logging.info(f"  [US] found {len(jobs)} jobs")

            for job in jobs:
                title = job.get("title", "N/A")
                company = job.get("company", {}).get("display_name", "N/A")

                all_jobs.append({
                    "title": title,
                    "company": company,
                    "location": "Remote",
                    "description": job.get("description", ""),
                    "link": job.get("redirect_url", "N/A"),
                    "posted_date": job.get("created", "N/A"),
                    "source": "Adzuna",
                    "salary_min": job.get("salary_min", "N/A"),
                    "salary_max": job.get("salary_max", "N/A"),
                    "country": "US",
                })

            time.sleep(1)

        except requests.exceptions.Timeout:
            logging.error(f"  [Adzuna] Timeout for {role}")
        except requests.exceptions.RequestException as e:
            logging.error(f"  [Adzuna] Request failed: {e}")

    logging.info(f"[Adzuna] Total jobs fetched: {len(all_jobs)}")
    return all_jobs


def fetch_jobs():
    """
    Master fetch function — combines jobs from all sources.
    Easy to extend by adding new sources here later.
    """
    config = load_config()
    all_jobs = []

    # Source 1: JSearch
    jsearch_jobs = fetch_jsearch_jobs(config)
    all_jobs.extend(jsearch_jobs)

    # Source 2: Adzuna
    adzuna_jobs = fetch_adzuna_jobs(config)
    all_jobs.extend(adzuna_jobs)

    logging.info(f"Total jobs from all sources: {len(all_jobs)}")
    return all_jobs