import json
import sqlite3
from contextlib import closing


def save_jobs(jobs, database_path="jobs.db"):
    database_rows = []

    for job in jobs:
        if type(job.get("id")) is not int or job["id"] <= 0:
            raise ValueError("Job ID must be a positive integer.")
        tags = job.get("tags", [])

        if not isinstance(tags, list):
            raise ValueError("Job tags must be a list.")

        database_rows.append({
            **job,
            "tags": json.dumps(tags, ensure_ascii=False),
        })

    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            # 1. Create the table.
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    url TEXT NOT NULL
                )
                """
            )

            # 2. Insert new jobs or update existing ones.
            connection.executemany(
                """
                INSERT INTO jobs (
                    id, title, company_name, category, tags, url
                )
                VALUES (
                    :id, :title, :company_name, :category, :tags, :url
                )
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    company_name = excluded.company_name,
                    category = excluded.category,
                    tags = excluded.tags,
                    url = excluded.url
                """,
                database_rows,
            )

        # Changes are committed before reading.

        # 3. Retrieve all saved jobs.
        rows = connection.execute(
            """
            SELECT id, title, company_name, category, tags, url
            FROM jobs
            ORDER BY id
            """
        ).fetchall()

        # 4. Print each row.
        print(f"\nTotal jobs in database: {len(rows)}")

        for row in rows:
            print(row)

    # The connection is automatically closed here.
