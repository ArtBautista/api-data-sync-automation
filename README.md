# API Data Sync Automation

A Python learning project that fetches remote job listings from the [Remotive API](https://remotive.com/api/remote-jobs), filters the Writing category, validates and transforms JSON, and saves the results to SQLite.

The project works with **jobs**, rather than user accounts. It demonstrates API requests, dictionaries and lists, validation, SQL transactions, and automated testing.

## What happens when you run it

1. `fetch_jobs()` sends a GET request with a 20-second timeout, checks the HTTP response, parses JSON, and verifies that `jobs` is a list.
2. `filter_jobs_by_category()` compares category names after trimming whitespace and ignoring letter case.
3. `transform_jobs()` selects `id`, `title`, `company_name`, `category`, `tags`, and `url`. Invalid records are skipped.
4. `main.py` prints the selected jobs as JSON.
5. `save_jobs()` creates the SQLite table if needed and inserts or updates each record by its API ID.
6. The application prints the stored rows and the number of selected jobs saved or updated.

## Installation

Use Python 3.12 (the version used for local verification). Clone the repository, then open the project directory:

```bash
git clone https://github.com/ArtBautista/api-data-sync-automation.git
cd api-data-sync-automation
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the application and test dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

For application-only installation, use `requirements.txt` instead.

## Run

Run from the project root:

```bash
python main.py
```

Internet access is required for the application. No API key is configured. Change `"Writing"` in `main.py` to select a different category. Category matching is exact after trimming and case normalization; it is not tag matching.

The application creates `jobs.db` in the current working directory. Zero matching jobs is a valid result. Database files are excluded from Git.

## Data validation

- The API response must be an object containing a `jobs` list; otherwise the fetch raises `ValueError`.
- A job must be a dictionary with a positive integer ID. Booleans and numeric strings do not count as valid IDs.
- Title, company name, category, and URL must be non-empty strings. URL syntax is not validated.
- Missing `tags` defaults to `[]`. Explicit `None`, non-list tags, or non-string tag entries cause the job to be skipped.
- Extra API fields are discarded. Stored text retains its original spelling and whitespace.

## SQLite and duplicate prevention

The `jobs` table has an integer primary key (`id`) and text columns for title, company name, category, tags, and URL. Tags are serialized with `json.dumps()` because SQLite does not directly store Python lists. Use `json.loads()` to turn stored tag text back into a list.

Parameterized SQL binds values safely. `ON CONFLICT(id) DO UPDATE` updates an existing row instead of inserting a duplicate. Repeating the same run therefore preserves one row per API ID. The database function rejects invalid IDs even when called directly.

A batch is committed on success and rolled back on database failure. The connection is closed automatically. Jobs no longer returned by the API are **not deleted**; this is an accumulating local store, not an exact mirror of current vacancies.

## Error handling

HTTP errors, connection failures, timeouts, invalid JSON/response shapes, and SQLite errors are reported by `main.py` and re-raised so the command exits unsuccessfully. There are no automatic retries or scheduled runs. Run manually and respect Remotive's API usage terms and attribution requirements before redistributing data.

## Automated tests

```bash
python -m pytest -v
```

Tests mock HTTP requests and use temporary SQLite databases, so they require no live API or existing `jobs.db`. Coverage includes:

- Successful fetches, timeout configuration, connection failures, HTTP errors, and malformed responses.
- Category filtering and input validation.
- Field selection, missing/invalid tags, and required fields/IDs.
- SQLite tag round trips, repeated-ID updates, and transaction rollback.

Local verification: **29 tests passed** on Python 3.12. This verifies the application logic with mocked responses; it is not a live API availability check. CI/CD is not configured in this version.

## Files

| File | Purpose |
| --- | --- |
| `main.py` | Runs fetch, filter, transform, display, and save |
| `src/api_client.py` | HTTP request, category filtering, record validation |
| `src/database.py` | SQLite persistence and stored-row display |
| `test/test_api_client.py` | Original transformation tests |
| `test/test_sync.py` | Request, validation, and database regression tests |
| `requirements.txt` | Application dependency |
| `requirements-dev.txt` | Application and test dependencies |
| `.gitignore` | Excludes databases, environments, secrets, and caches |

## Readiness checklist

- [x] Fetch records from a public REST API (job listings)
- [x] Parse and transform JSON data
- [x] Handle request failures and timeouts
- [x] Store records in SQLite
- [x] Prevent duplicate records on repeated runs
- [x] Write automated unit tests
- [x] Document installation and execution steps
- [x] Publish a GitHub repository with README

