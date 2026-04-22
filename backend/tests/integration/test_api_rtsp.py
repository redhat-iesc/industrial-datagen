import pytest


class TestRTSPConfig:
    @pytest.mark.asyncio
    async def test_get_config_returns_all_process_types(self, client) -> None:
        resp = await client.get("/api/rtsp/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "refinery" in data
        assert "chemical" in data
        assert "pulp" in data
        assert "pharma" in data
        assert "rotating" in data
        for cfg in data.values():
            assert cfg["url"] is None
            assert cfg["status"] == "offline"

    @pytest.mark.asyncio
    async def test_set_url(self, client) -> None:
        resp = await client.put(
            "/api/rtsp/config/refinery",
            json={"url": "rtsp://cam:554/stream"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["url"] == "rtsp://cam:554/stream"
        assert data["status"] == "offline"

    @pytest.mark.asyncio
    async def test_clear_url(self, client) -> None:
        await client.put("/api/rtsp/config/refinery", json={"url": "rtsp://cam:554/s"})
        resp = await client.put("/api/rtsp/config/refinery", json={"url": None})
        assert resp.status_code == 200
        assert resp.json()["url"] is None

    @pytest.mark.asyncio
    async def test_set_url_invalid_process_type(self, client) -> None:
        resp = await client.put("/api/rtsp/config/invalid", json={"url": "rtsp://x"})
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_config_persists_across_gets(self, client) -> None:
        await client.put("/api/rtsp/config/chemical", json={"url": "rtsp://cam2:554/s"})
        resp = await client.get("/api/rtsp/config")
        assert resp.json()["chemical"]["url"] == "rtsp://cam2:554/s"


class TestStreamControl:
    @pytest.mark.asyncio
    async def test_start_no_url_returns_400(self, client) -> None:
        resp = await client.post("/api/rtsp/refinery/start")
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_start_invalid_process_type(self, client) -> None:
        resp = await client.post("/api/rtsp/invalid/start")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_stop_returns_offline(self, client) -> None:
        resp = await client.post("/api/rtsp/refinery/stop")
        assert resp.status_code == 200
        data = resp.json()
        assert data["processType"] == "refinery"
        assert data["status"] == "offline"

    @pytest.mark.asyncio
    async def test_stop_invalid_process_type(self, client) -> None:
        resp = await client.post("/api/rtsp/invalid/stop")
        assert resp.status_code == 404


class TestHLSServing:
    @pytest.mark.asyncio
    async def test_playlist_not_found(self, client) -> None:
        resp = await client.get("/api/rtsp/refinery/stream.m3u8")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_playlist_invalid_process_type(self, client) -> None:
        resp = await client.get("/api/rtsp/invalid/stream.m3u8")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_segment_invalid_name(self, client) -> None:
        resp = await client.get("/api/rtsp/refinery/../../etc/passwd")
        assert resp.status_code in (400, 404)

    @pytest.mark.asyncio
    async def test_segment_valid_name_not_found(self, client) -> None:
        resp = await client.get("/api/rtsp/refinery/seg000.ts")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_segment_served_when_exists(self, client) -> None:
        manager = client._transport.app.state.app_context.rtsp_manager
        stream_dir = manager.get_stream_dir("refinery")
        stream_dir.mkdir(parents=True, exist_ok=True)
        (stream_dir / "seg000.ts").write_bytes(b"\x00" * 188)

        resp = await client.get("/api/rtsp/refinery/seg000.ts")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "video/mp2t"

    @pytest.mark.asyncio
    async def test_playlist_served_when_exists(self, client) -> None:
        manager = client._transport.app.state.app_context.rtsp_manager
        stream_dir = manager.get_stream_dir("refinery")
        stream_dir.mkdir(parents=True, exist_ok=True)
        (stream_dir / "stream.m3u8").write_text("#EXTM3U\n#EXT-X-VERSION:3\n")

        resp = await client.get("/api/rtsp/refinery/stream.m3u8")
        assert resp.status_code == 200
        assert "mpegurl" in resp.headers["content-type"]
