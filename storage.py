import gspread
from google.oauth2.service_account import Credentials
import logging
from datetime import datetime

def get_sheet():
    """
    Authenticate with Google Sheets API and return the worksheet.
    """
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)

    import json
    config = json.load(open("config.json"))
    sheet = client.open_by_key(config["sheet_id"])

    # Use first worksheet
    return sheet.sheet1


def setup_headers(worksheet):
    """
    Add header row to the sheet if it doesn't exist yet.
    """
    headers = [
        "Title", "Company", "Location", "Score",
        "Source", "Salary Min", "Salary Max",
        "Posted Date", "Apply Link", "Status", "Notes", "Added On"
    ]

    first_row = worksheet.row_values(1)
    if not first_row:
        worksheet.append_row(headers)
        # Make headers bold
        worksheet.format("A1:L1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.8}
        })
        logging.info("Headers added to sheet")


def get_existing_jobs(worksheet):
    """
    Get all jobs already in the sheet to avoid adding duplicates.
    Returns a set of 'title|company' identifiers.
    """
    records = worksheet.get_all_records()
    existing = set()
    for record in records:
        key = f"{record.get('Title','').lower()}|{record.get('Company','').lower()}"
        existing.add(key)
    return existing


def save_to_sheets(jobs):
    """
    Save scored jobs to Google Sheet.
    Skips jobs already in the sheet.
    """
    logging.info("Connecting to Google Sheets...")
    worksheet = get_sheet()
    setup_headers(worksheet)

    existing_jobs = get_existing_jobs(worksheet)
    new_jobs_added = 0

    for job in jobs:
        # Check if job already exists in sheet
        key = f"{job.get('title','').lower()}|{job.get('company','').lower()}"
        if key in existing_jobs:
            continue

        row = [
            job.get("title", "N/A"),
            job.get("company", "N/A"),
            job.get("location", "Remote"),
            job.get("score", 0),
            job.get("source", "N/A"),
            job.get("salary_min", "N/A"),
            job.get("salary_max", "N/A"),
            job.get("posted_date", "N/A"),
            job.get("link", "N/A"),
            "Not Applied",        # Default status — you update this manually
            "",                   # Notes column — you fill this in
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ]

        worksheet.append_row(row)
        new_jobs_added += 1

    logging.info(f"New jobs added to sheet: {new_jobs_added}")
    logging.info(f"Skipped (already in sheet): {len(jobs) - new_jobs_added}")
    return new_jobs_added