import asyncio


async def test_start_simulation(client):
    resp = await client.post("/api/simulation/start", json={
        "processType": "refinery",
        "parameters": {},
        "intervalMs": 100,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["processType"] == "refinery"
    assert data["status"] == "running"
    assert "id" in data

    await client.post(f"/api/simulation/{data['id']}/stop")


async def test_start_simulation_unknown_type(client):
    resp = await client.post("/api/simulation/start", json={
        "processType": "unknown",
    })
    assert resp.status_code == 400


async def test_stop_simulation(client):
    resp = await client.post("/api/simulation/start", json={
        "processType": "chemical",
        "intervalMs": 100,
    })
    sim_id = resp.json()["id"]

    resp = await client.post(f"/api/simulation/{sim_id}/stop")
    assert resp.status_code == 200
    assert resp.json()["status"] == "stopped"


async def test_get_current_after_steps(client):
    resp = await client.post("/api/simulation/start", json={
        "processType": "refinery",
        "intervalMs": 50,
    })
    sim_id = resp.json()["id"]

    await asyncio.sleep(0.2)

    resp = await client.get(f"/api/simulation/{sim_id}/current")
    assert resp.status_code == 200
    data = resp.json()
    assert "simulation" in data
    assert data["current"] is not None

    await client.post(f"/api/simulation/{sim_id}/stop")


async def test_get_history(client):
    resp = await client.post("/api/simulation/start", json={
        "processType": "pulp",
        "intervalMs": 50,
    })
    sim_id = resp.json()["id"]

    await asyncio.sleep(0.3)

    resp = await client.get(f"/api/simulation/{sim_id}/history")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert len(data["data"]) > 0

    await client.post(f"/api/simulation/{sim_id}/stop")


async def test_update_parameters(client):
    resp = await client.post("/api/simulation/start", json={
        "processType": "refinery",
        "intervalMs": 100,
    })
    sim_id = resp.json()["id"]

    resp = await client.patch(f"/api/simulation/{sim_id}/parameters", json={
        "parameters": {"crudeTemp": 400},
    })
    assert resp.status_code == 200
    assert resp.json()["parameters"]["crudeTemp"] == 400

    await client.post(f"/api/simulation/{sim_id}/stop")


async def test_inject_fault_rotating(client):
    resp = await client.post("/api/simulation/start", json={
        "processType": "rotating",
        "intervalMs": 100,
    })
    sim_id = resp.json()["id"]

    resp = await client.post(f"/api/simulation/{sim_id}/fault", json={
        "faultType": "bearing_fault",
    })
    assert resp.status_code == 200
    assert resp.json()["faultType"] == "bearing_fault"

    await client.post(f"/api/simulation/{sim_id}/stop")


async def test_inject_fault_non_rotating_fails(client):
    resp = await client.post("/api/simulation/start", json={
        "processType": "refinery",
        "intervalMs": 100,
    })
    sim_id = resp.json()["id"]

    resp = await client.post(f"/api/simulation/{sim_id}/fault", json={
        "faultType": "bearing_fault",
    })
    assert resp.status_code == 400

    await client.post(f"/api/simulation/{sim_id}/stop")


async def test_list_simulations(client):
    resp = await client.post("/api/simulation/start", json={
        "processType": "refinery",
        "intervalMs": 100,
    })
    sim_id = resp.json()["id"]

    resp = await client.get("/api/simulations")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    await client.post(f"/api/simulation/{sim_id}/stop")


async def test_simulation_not_found(client):
    resp = await client.get("/api/simulation/nonexistent/current")
    assert resp.status_code == 404
