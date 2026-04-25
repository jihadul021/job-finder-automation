import logging

def is_relevant(job, config):
    """
    Check if a job is relevant based on role and keyword matching.
    Returns True if the job matches, False otherwise.
    """
    title_lower = job.get("title", "").lower()
    description_lower = job.get("description", "").lower()
    searchable_text = title_lower + " " + description_lower

    # Reject if title contains any excluded keywords (e.g. senior, lead)
    exclude = config.get("exclude_keywords", [])
    if any(ex.lower() in title_lower for ex in exclude):
        return False

    # Check if any of the user's roles appear in the job title
    role_match = any(role.lower() in title_lower for role in config["roles"])

    # Check if any skill keywords appear in the full text
    keyword_match = any(kw.lower() in searchable_text for kw in config["keywords"])

    return role_match and keyword_match


def remove_duplicates(jobs):
    """
    Remove duplicate jobs based on title + company combination.
    """
    seen = set()
    unique_jobs = []

    for job in jobs:
        identifier = (
            job.get("title", "").lower().strip() + "|" +
            job.get("company", "").lower().strip()
        )

        if identifier not in seen:
            seen.add(identifier)
            unique_jobs.append(job)

    duplicates_removed = len(jobs) - len(unique_jobs)
    logging.info(f"Duplicates removed: {duplicates_removed}")
    return unique_jobs


def filter_jobs(jobs, config):
    """
    Main filter function:
    1. Remove duplicates
    2. Exclude senior/lead roles
    3. Keep only relevant entry level jobs
    """
    logging.info(f"Starting filter — total jobs before: {len(jobs)}")
    jobs = remove_duplicates(jobs)
    relevant = [job for job in jobs if is_relevant(job, config)]
    logging.info(f"Relevant jobs after filtering: {len(relevant)}")
    return relevant

