async def test_list_processes(client):
    resp = await client.get("/api/processes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    names = {p["name"] for p in data}
    assert names == {"refinery", "chemical", "pulp", "pharma", "rotating"}


async def test_each_process_has_parameters_and_outputs(client):
    resp = await client.get("/api/processes")
    for process in resp.json():
        assert "parameters" in process
        assert "outputs" in process
        assert len(process["parameters"]) > 0
        assert len(process["outputs"]) > 0


async def test_get_process_schema(client):
    resp = await client.get("/api/processes/refinery/schema")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "refinery"
    assert "parameters" in data
    assert "outputs" in data


async def test_get_process_schema_unknown_type(client):
    resp = await client.get("/api/processes/unknown/schema")
    assert resp.status_code == 404
