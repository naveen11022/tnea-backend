"""Tests for all lookup/GET endpoints."""


def test_get_branch_category(client):
    resp = client.get("/api/get_branch_category")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert "Engineering" in data


def test_get_branch(client):
    resp = client.get("/api/get_branch")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Each item is [branch_code, branch_name]
    assert isinstance(data[0], list)
    assert len(data[0]) == 2


def test_get_year(client):
    resp = client.get("/api/get_year")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert 2023 in data
    assert 2022 in data
    # Should be descending
    assert data == sorted(data, reverse=True)


def test_get_region(client):
    resp = client.get("/api/get_region")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert "Chennai" in data


def test_get_category(client):
    resp = client.get("/api/get_category")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert "OC" in data or "BC" in data


def test_get_college_type(client):
    resp = client.get("/api/college_type")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert "Government" in data or "Private" in data
