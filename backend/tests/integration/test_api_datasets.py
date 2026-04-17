async def test_generate_dataset(client):
    resp = await client.post("/api/datasets/generate", json={
        "processType": "refinery",
        "samples": 50,
        "includeAnomalies": True,
        "format": "csv",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["processType"] == "refinery"
    assert data["status"] == "ready"
    assert data["samples"] == 50


async def test_generate_dataset_unknown_type(client):
    resp = await client.post("/api/datasets/generate", json={
        "processType": "unknown",
        "samples": 10,
    })
    assert resp.status_code == 400


async def test_list_datasets(client):
    await client.post("/api/datasets/generate", json={
        "processType": "chemical",
        "samples": 10,
    })
    resp = await client.get("/api/datasets")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_download_dataset_csv(client):
    gen_resp = await client.post("/api/datasets/generate", json={
        "processType": "refinery",
        "samples": 10,
        "format": "csv",
    })
    dataset_id = gen_resp.json()["id"]

    resp = await client.get(f"/api/datasets/{dataset_id}/download?format=csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    lines = resp.text.strip().split("\n")
    assert len(lines) == 11  # header + 10 rows


async def test_download_dataset_json(client):
    gen_resp = await client.post("/api/datasets/generate", json={
        "processType": "pulp",
        "samples": 5,
        "format": "json",
    })
    dataset_id = gen_resp.json()["id"]

    resp = await client.get(f"/api/datasets/{dataset_id}/download?format=json")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5


async def test_get_dataset_status(client):
    gen_resp = await client.post("/api/datasets/generate", json={
        "processType": "pharma",
        "samples": 10,
    })
    dataset_id = gen_resp.json()["id"]

    resp = await client.get(f"/api/datasets/{dataset_id}/status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


async def test_delete_dataset(client):
    gen_resp = await client.post("/api/datasets/generate", json={
        "processType": "rotating",
        "samples": 10,
    })
    dataset_id = gen_resp.json()["id"]

    resp = await client.delete(f"/api/datasets/{dataset_id}")
    assert resp.status_code == 200

    resp = await client.get(f"/api/datasets/{dataset_id}/status")
    assert resp.status_code == 404


async def test_download_nonexistent_dataset(client):
    resp = await client.get("/api/datasets/nonexistent/download")
    assert resp.status_code == 404
