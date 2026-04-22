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


async def test_generated_dataset_has_temporal_data(client):
    """API-generated datasets should have accumulating state and sequential timestamps."""
    gen_resp = await client.post("/api/datasets/generate", json={
        "processType": "refinery",
        "samples": 50,
        "includeAnomalies": False,
        "format": "json",
    })
    dataset_id = gen_resp.json()["id"]

    resp = await client.get(f"/api/datasets/{dataset_id}/download?format=json")
    data = resp.json()

    assert len(data) == 50
    # Timestamps must be sequential
    timestamps = [row["timestamp"] for row in data]
    assert timestamps == list(range(50))
    # totalProcessed must accumulate (non-decreasing)
    for i in range(1, len(data)):
        assert data[i]["totalProcessed"] >= data[i - 1]["totalProcessed"]


async def test_large_dataset_generates(client):
    """Verify the API handles large dataset generation (10k samples)."""
    gen_resp = await client.post("/api/datasets/generate", json={
        "processType": "chemical",
        "samples": 10000,
        "includeAnomalies": True,
        "format": "csv",
    })
    assert gen_resp.status_code == 200
    data = gen_resp.json()
    assert data["status"] == "ready"
    assert data["samples"] == 10000

    # Download and validate
    resp = await client.get(f"/api/datasets/{data['id']}/download?format=csv")
    assert resp.status_code == 200
    lines = resp.text.strip().split("\n")
    assert len(lines) == 10001  # header + data
