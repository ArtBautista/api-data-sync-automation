from src.api_client import transform_jobs


def test_transform_jobs():
    sample_data = [
        {
            "id": 1,
            "title": "Software Example",
            "company_name": "Coalition Example",
            "category": "Software Development",
            "tags": [],
            "url": "https://example.com/jobs/1",
            "description": "This field should be excluded.",
        }
    ]

    result = transform_jobs(sample_data)

    assert result == [
        {
            "id": 1,
            "title": "Software Example",
            "company_name": "Coalition Example",
            "category": "Software Development",
            "tags": [],
            "url": "https://example.com/jobs/1",
        }
    ]


def test_none_tags_is_skipped():
    sample_data = [
        {
            "id": 1,
            "title": "Software Example",
            "company_name": "Coalition Example",
            "category": "Software Development",
            "tags": None,
            "url": "https://example.com/jobs/1",
        }
    ]

    assert transform_jobs(sample_data) == []


def test_missing_tags_defaults_to_empty_list():
    sample_data = [
        {
            "id": 1,
            "title": "Software Example",
            "company_name": "Coalition Example",
            "category": "Software Development",
            "url": "https://example.com/jobs/1",
        }
    ]

    result = transform_jobs(sample_data)

    assert len(result) == 1
    assert result[0]["tags"] == []