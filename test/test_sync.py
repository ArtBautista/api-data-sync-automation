import json
import sqlite3
from contextlib import closing
from unittest.mock import Mock

import pytest
import requests

from src.api_client import API_URL_JOBS, fetch_jobs, filter_jobs_by_category, transform_jobs
from src.database import save_jobs


@pytest.fixture
def job():
    return {
        'id': 1, 'title': 'Writer', 'company_name': 'Example',
        'category': 'Writing', 'tags': ['content'],
        'url': 'https://example.com/jobs/1',
    }


def test_fetch_jobs(monkeypatch, job):
    response = Mock()
    response.json.return_value = {'jobs': [job]}
    get = Mock(return_value=response)
    monkeypatch.setattr('src.api_client.requests.get', get)
    assert fetch_jobs() == [job]
    get.assert_called_once_with(API_URL_JOBS, timeout=20)
    response.raise_for_status.assert_called_once()


@pytest.mark.parametrize('error', [requests.Timeout, requests.ConnectionError])
def test_request_failure_propagates(monkeypatch, error):
    monkeypatch.setattr('src.api_client.requests.get', Mock(side_effect=error('Failure')))
    with pytest.raises(error):
        fetch_jobs()


def test_http_error_propagates(monkeypatch):
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError('503')
    monkeypatch.setattr('src.api_client.requests.get', Mock(return_value=response))
    with pytest.raises(requests.HTTPError):
        fetch_jobs()
    response.json.assert_not_called()


@pytest.mark.parametrize('payload', [[], {}, {'jobs': None}, {'jobs': {}}])
def test_invalid_response_rejected(monkeypatch, payload):
    response = Mock()
    response.json.return_value = payload
    monkeypatch.setattr('src.api_client.requests.get', Mock(return_value=response))
    with pytest.raises(ValueError):
        fetch_jobs()


def test_invalid_json_propagates(monkeypatch):
    response = Mock()
    response.json.side_effect = ValueError('Invalid JSON')
    monkeypatch.setattr('src.api_client.requests.get', Mock(return_value=response))
    with pytest.raises(ValueError):
        fetch_jobs()


def test_filter_category(job):
    assert filter_jobs_by_category([None, job, {**job, 'category': 'Design'}], ' writing ') == [job]


@pytest.mark.parametrize('category', ['', '  ', None])
def test_invalid_category(category):
    with pytest.raises(ValueError):
        filter_jobs_by_category([], category)


@pytest.mark.parametrize('job_id', [None, True, 0, -1, '1'])
def test_invalid_id_skipped(job, job_id):
    assert transform_jobs([{**job, 'id': job_id}]) == []


@pytest.mark.parametrize('field', ['title', 'company_name', 'category', 'url'])
def test_missing_required_field_skipped(job, field):
    del job[field]
    assert transform_jobs([job]) == []


def test_invalid_tag_skipped(job):
    assert transform_jobs([{**job, 'tags': [None]}]) == []


def test_upsert_and_tags_round_trip(tmp_path, job):
    path = tmp_path / 'jobs.db'
    save_jobs([job], path)
    updated = {**job, 'title': 'Senior Writer', 'tags': ['content', 'editing']}
    save_jobs([updated], path)
    save_jobs([updated], path)
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute('SELECT id, title, tags FROM jobs').fetchall()
    assert len(rows) == 1
    assert rows[0][:2] == (1, 'Senior Writer')
    assert json.loads(rows[0][2]) == ['content', 'editing']


def test_database_rejects_missing_id(tmp_path, job):
    del job['id']
    with pytest.raises(ValueError, match='ID'):
        save_jobs([job], tmp_path / 'jobs.db')


def test_batch_rolls_back_on_failure(tmp_path, job):
    path = tmp_path / 'jobs.db'
    save_jobs([job], path)
    with pytest.raises(sqlite3.IntegrityError):
        save_jobs([{**job, 'title': 'Changed'}, {**job, 'id': 2, 'title': None}], path)
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute('SELECT id, title FROM jobs').fetchall() == [(1, 'Writer')]
