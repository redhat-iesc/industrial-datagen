import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.rtsp import StreamStatus
from app.rtsp.manager import RTSPStreamManager


@pytest.fixture
def manager(tmp_path: Path) -> RTSPStreamManager:
    return RTSPStreamManager(base_dir=tmp_path / "rtsp-streams")


class TestURLConfig:
    def test_set_and_get_url(self, manager: RTSPStreamManager) -> None:
        manager.set_url("refinery", "rtsp://cam1:554/stream")
        config = manager.get_config("refinery")
        assert config["url"] == "rtsp://cam1:554/stream"
        assert config["status"] == StreamStatus.OFFLINE

    def test_clear_url(self, manager: RTSPStreamManager) -> None:
        manager.set_url("refinery", "rtsp://cam1:554/stream")
        manager.set_url("refinery", None)
        config = manager.get_config("refinery")
        assert config["url"] is None

    def test_get_config_no_url(self, manager: RTSPStreamManager) -> None:
        config = manager.get_config("refinery")
        assert config["url"] is None
        assert config["status"] == StreamStatus.OFFLINE

    def test_get_all_configs(self, manager: RTSPStreamManager) -> None:
        manager.set_url("refinery", "rtsp://cam1:554/stream")
        configs = manager.get_all_configs(["refinery", "chemical", "pulp"])
        assert len(configs) == 3
        assert configs["refinery"]["url"] == "rtsp://cam1:554/stream"
        assert configs["chemical"]["url"] is None


class TestStreamLifecycle:
    @pytest.mark.asyncio
    async def test_start_stream_no_url_raises(self, manager: RTSPStreamManager) -> None:
        with pytest.raises(ValueError, match="No RTSP URL configured"):
            await manager.start_stream("refinery")

    @pytest.mark.asyncio
    async def test_start_stream_creates_process(self, manager: RTSPStreamManager) -> None:
        manager.set_url("refinery", "rtsp://cam1:554/stream")

        mock_process = MagicMock()
        mock_process.returncode = None
        mock_process.stderr = AsyncMock()
        mock_process.stderr.readline = AsyncMock(return_value=b"")
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.terminate = MagicMock()

        patch_target = "app.rtsp.manager.asyncio.create_subprocess_exec"
        with patch(patch_target, return_value=mock_process) as mock_exec:
            state = await manager.start_stream("refinery")

            mock_exec.assert_called_once()
            call_args = mock_exec.call_args[0]
            assert call_args[0] == "ffmpeg"
            assert "-rtsp_transport" in call_args
            assert "rtsp://cam1:554/stream" in call_args

            assert state.status == StreamStatus.STARTING
            assert state.started_at is not None

        await manager.stop_all()

    @pytest.mark.asyncio
    async def test_stop_stream_terminates_process(self, manager: RTSPStreamManager) -> None:
        manager.set_url("refinery", "rtsp://cam1:554/stream")

        mock_process = MagicMock()
        mock_process.returncode = None
        mock_process.stderr = AsyncMock()
        mock_process.stderr.readline = AsyncMock(return_value=b"")
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.terminate = MagicMock()
        mock_process.kill = MagicMock()

        with patch("app.rtsp.manager.asyncio.create_subprocess_exec", return_value=mock_process):
            await manager.start_stream("refinery")
            await asyncio.sleep(0.05)
            await manager.stop_stream("refinery")

            mock_process.terminate.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_stream_not_started(self, manager: RTSPStreamManager) -> None:
        await manager.stop_stream("refinery")

    @pytest.mark.asyncio
    async def test_stop_all(self, manager: RTSPStreamManager) -> None:
        manager.set_url("refinery", "rtsp://cam1:554/s1")
        manager.set_url("chemical", "rtsp://cam2:554/s2")

        mock_process = MagicMock()
        mock_process.returncode = None
        mock_process.stderr = AsyncMock()
        mock_process.stderr.readline = AsyncMock(return_value=b"")
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.terminate = MagicMock()

        with patch("app.rtsp.manager.asyncio.create_subprocess_exec", return_value=mock_process):
            await manager.start_stream("refinery")
            await manager.start_stream("chemical")
            await asyncio.sleep(0.05)
            await manager.stop_all()

            assert len(manager._streams) == 0

    @pytest.mark.asyncio
    async def test_restart_stops_existing(self, manager: RTSPStreamManager) -> None:
        manager.set_url("refinery", "rtsp://cam1:554/stream")

        mock_process = MagicMock()
        mock_process.returncode = None
        mock_process.stderr = AsyncMock()
        mock_process.stderr.readline = AsyncMock(return_value=b"")
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.terminate = MagicMock()

        with patch("app.rtsp.manager.asyncio.create_subprocess_exec", return_value=mock_process):
            await manager.start_stream("refinery")
            await asyncio.sleep(0.05)
            await manager.start_stream("refinery")

            mock_process.terminate.assert_called()

        await manager.stop_all()


class TestMonitorProcess:
    @pytest.mark.asyncio
    async def test_status_transitions_to_streaming(self, manager: RTSPStreamManager) -> None:
        manager.set_url("refinery", "rtsp://cam1:554/stream")

        hold = asyncio.Event()

        async def readline_side_effect() -> bytes:
            lines = getattr(readline_side_effect, "_lines", None)
            if lines is None:
                readline_side_effect._lines = iter([
                    b"Input #0, rtsp, from 'rtsp://cam1:554/stream':\n",
                    b"frame=   24 fps= 24 q=-1.0 size=   256kB time=00:00:01.00\n",
                ])
                lines = readline_side_effect._lines
            try:
                return next(lines)
            except StopIteration:
                await hold.wait()
                return b""

        mock_process = MagicMock()
        mock_process.returncode = None
        mock_process.stderr = AsyncMock()
        mock_process.stderr.readline = readline_side_effect
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.terminate = MagicMock()

        with patch("app.rtsp.manager.asyncio.create_subprocess_exec", return_value=mock_process):
            state = await manager.start_stream("refinery")
            await asyncio.sleep(0.1)

            assert state.status == StreamStatus.STREAMING

            hold.set()

        await manager.stop_all()

    @pytest.mark.asyncio
    async def test_error_on_nonzero_exit(self, manager: RTSPStreamManager) -> None:
        manager.set_url("refinery", "rtsp://cam1:554/stream")

        mock_process = MagicMock()
        mock_process.returncode = None
        mock_process.stderr = AsyncMock()
        mock_process.stderr.readline = AsyncMock(return_value=b"")
        mock_process.wait = AsyncMock(return_value=1)
        mock_process.terminate = MagicMock()

        with patch("app.rtsp.manager.asyncio.create_subprocess_exec", return_value=mock_process):
            state = await manager.start_stream("refinery")
            await asyncio.sleep(0.1)

            assert state.status == StreamStatus.ERROR
            assert "exited with code 1" in (state.error or "")

        manager._streams.clear()


class TestValidation:
    def test_valid_segment_names(self) -> None:
        assert RTSPStreamManager.validate_segment_name("seg000.ts")
        assert RTSPStreamManager.validate_segment_name("seg001.ts")
        assert RTSPStreamManager.validate_segment_name("seg999.ts")

    def test_invalid_segment_names(self) -> None:
        assert not RTSPStreamManager.validate_segment_name("seg0001.ts")
        assert not RTSPStreamManager.validate_segment_name("../seg000.ts")
        assert not RTSPStreamManager.validate_segment_name("seg000.ts.bak")
        assert not RTSPStreamManager.validate_segment_name("stream.m3u8")
        assert not RTSPStreamManager.validate_segment_name("")
        assert not RTSPStreamManager.validate_segment_name("../../etc/passwd")

    def test_base_dir_created(self, tmp_path: Path) -> None:
        base = tmp_path / "new" / "rtsp"
        RTSPStreamManager(base_dir=base)
        assert base.exists()
