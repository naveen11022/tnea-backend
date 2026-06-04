"""Tests for the POST /api/fetch_data endpoint."""


def test_fetch_data_no_filters(client):
    resp = client.post("/api/fetch_data", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
    # Verify response shape
    keys = {"year", "aggr_mark", "community", "college_code", "college_name",
            "branch_name", "general_rank", "community_rank", "round", "allotted_category"}
    assert keys.issubset(data[0].keys())


def test_fetch_data_filter_year(client):
    resp = client.post("/api/fetch_data", json={"Year": [2023]})
    assert resp.status_code == 200
    data = resp.json()
    assert all(r["year"] == 2023 for r in data)


def test_fetch_data_filter_community(client):
    resp = client.post("/api/fetch_data", json={"Community": ["OC"]})
    assert resp.status_code == 200
    data = resp.json()
    assert all(r["community"] == "OC" for r in data)


def test_fetch_data_cutoff_gt(client):
    resp = client.post("/api/fetch_data", json={"Cutoff": [">"], "FirstValue": [190.0]})
    assert resp.status_code == 200
    data = resp.json()
    assert all(r["aggr_mark"] > 190.0 for r in data)


def test_fetch_data_cutoff_between(client):
    resp = client.post("/api/fetch_data", json={
        "Cutoff": ["between"], "FirstValue": [175.0], "SecondValue": [200.0]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert all(175.0 <= r["aggr_mark"] <= 200.0 for r in data)


def test_fetch_data_ordered_by_year_desc(client):
    resp = client.post("/api/fetch_data", json={})
    assert resp.status_code == 200
    data = resp.json()
    years = [r["year"] for r in data]
    assert years == sorted(years, reverse=True)


def test_fetch_data_no_results(client):
    resp = client.post("/api/fetch_data", json={"Year": [1900]})
    assert resp.status_code == 200
    assert resp.json() == []
