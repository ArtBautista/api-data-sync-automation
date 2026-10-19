import requests


API_URL_JOBS = "https://remotive.com/api/remote-jobs"


def fetch_jobs():
    response = requests.get(API_URL_JOBS, timeout=20)
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict):
        raise ValueError("Expected the response to be a dictionary.")

    jobs = data.get("jobs")

    if not isinstance(jobs, list):
        raise ValueError("Expected the response to contain a jobs list.")

    return jobs


def filter_jobs_by_category(jobs, target_category):
    if not isinstance(target_category, str) or not target_category.strip():
        raise ValueError("The target category must be a non-empty string.")

    target_category = target_category.strip().lower()
    filtered_jobs = []

    for job in jobs:
        if not isinstance(job, dict):
            continue

        category = job.get("category")

        if (
            isinstance(category, str)
            and category.strip().lower() == target_category
        ):
            filtered_jobs.append(job)

    return filtered_jobs


def transform_jobs(jobs):
    transformed = []

    for job in jobs:
        if not isinstance(job, dict):
            continue

        tags = job.get("tags", [])

        # A stable API ID is required for repeatable database updates.
        if type(job.get("id")) is not int or job["id"] <= 0:
            continue

        required_fields = ("title", "company_name", "category", "url")
        if any(
            not isinstance(job.get(field), str) or not job[field].strip()
            for field in required_fields
        ):
            continue

        # None is not a list, so skip this job.
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            continue

        transformed.append({
            "id": job.get("id"),
            "title": job.get("title"),
            "company_name": job.get("company_name"),
            "category": job.get("category"),
            "tags": tags,
            "url": job.get("url"),
        })

    return transformed
