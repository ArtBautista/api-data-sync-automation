import json
import sqlite3

import requests

from src.api_client import (
    fetch_jobs,
    filter_jobs_by_category,
    transform_jobs,
)
from src.database import save_jobs


def main():
    try:
        # 1. Fetch jobs from the API.
        jobs = fetch_jobs()

        # 2. Keep jobs in the Writing category.
        matching_jobs = filter_jobs_by_category(jobs, "Writing")

        # 3. Select the fields to store.
        selected_jobs = transform_jobs(matching_jobs)

        # 4. Display the results.
        print(f"Matching jobs: {len(selected_jobs)}")
        print(json.dumps(selected_jobs, indent=2, ensure_ascii=False))

        # 5. Insert new jobs or update existing ones.
        save_jobs(selected_jobs)

        print(f"Successfully saved or updated {len(selected_jobs)} jobs.")

    except (requests.RequestException, ValueError, sqlite3.Error) as error:
        print(f"Failed to retrieve, process, or save jobs: {error}")
        raise


if __name__ == "__main__":
    main()