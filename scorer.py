import logging

def score_job(job, config):
    """
    Score a job based on keyword matches in title and description.
    Title matches are worth more (3 points) than description matches (1 point).
    Returns an integer score.
    """
    score = 0
    title_lower = job.get("title", "").lower()
    description_lower = job.get("description", "").lower()

    for keyword in config["keywords"]:
        kw = keyword.lower()

        # Title match is worth 3 points — title is most important signal
        if kw in title_lower:
            score += 3

        # Description match is worth 1 point
        if kw in description_lower:
            score += 1

    # Bonus points for explicitly junior/intern signals in title
    junior_signals = ["intern", "junior", "entry level", "graduate", "fresher"]
    for signal in junior_signals:
        if signal in title_lower:
            score += 5

    # Bonus if salary info is available (means listing is more complete)
    if job.get("salary_min") and job.get("salary_min") != "N/A":
        score += 2

    return score


def score_jobs(jobs, config):
    """
    Score all jobs and return them sorted by score (highest first).
    """
    logging.info(f"Scoring {len(jobs)} jobs...")

    for job in jobs:
        job["score"] = score_job(job, config)

    # Sort by score descending
    sorted_jobs = sorted(jobs, key=lambda x: x["score"], reverse=True)

    logging.info(f"Top job: '{sorted_jobs[0]['title']}' with score {sorted_jobs[0]['score']}")
    return sorted_jobs