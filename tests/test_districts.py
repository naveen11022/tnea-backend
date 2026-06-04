"""Tests for the districts endpoint."""


def test_get_districts_valid_region(client):
    resp = client.post("/api/districts", json={"District": ["Chennai"]})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert "Chennai" in data


def test_get_districts_unknown_region(client):
    resp = client.post("/api/districts", json={"District": ["NonExistentRegion"]})
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_districts_multiple_regions(client):
    resp = client.post("/api/districts", json={"District": ["Chennai", "Coimbatore"]})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 2
