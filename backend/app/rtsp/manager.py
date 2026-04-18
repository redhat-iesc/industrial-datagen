import asyncio
import contextlib
import re
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from app.models.rtsp import StreamStatus


@dataclass
class StreamState:
    process: asyncio.subprocess.Process | None = None
    status: StreamStatus = StreamStatus.OFFLINE
    started_at: str | None = None
    error: str | None = None
    _monitor_task: asyncio.Task[None] | None = field(default=None, repr=False)


class RTSPStreamManager:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path("/tmp/rtsp-streams")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._configs: dict[str, str] = {}
        self._streams: dict[str, StreamState] = {}

    def set_url(self, process_type: str, url: str | None) -> None:
        if url is None:
            self._configs.pop(process_type, None)
        else:
            self._configs[process_type] = url

    def get_config(self, process_type: str) -> dict[str, str | None]:
        stream = self._streams.get(process_type)
        return {
            "url": self._configs.get(process_type),
            "status": stream.status if stream else StreamStatus.OFFLINE,
        }

    def get_all_configs(self, process_types: list[str]) -> dict[str, dict[str, str | None]]:
        return {pt: self.get_config(pt) for pt in process_types}

    async def start_stream(self, process_type: str) -> StreamState:
        url = self._configs.get(process_type)
        if not url:
            raise ValueError(f"No RTSP URL configured for {process_type}")

        if process_type in self._streams:
            await self.stop_stream(process_type)

        stream_dir = self.base_dir / process_type
        stream_dir.mkdir(parents=True, exist_ok=True)

        playlist = stream_dir / "stream.m3u8"
        seg_pattern = str(stream_dir / "seg%03d.ts")

        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", url,
            "-c:v", "copy",
            "-c:a", "aac",
            "-f", "hls",
            "-hls_time", "2",
            "-hls_list_size", "5",
            "-hls_flags", "delete_segments+append_list",
            "-hls_segment_filename", seg_pattern,
            str(playlist),
            stderr=asyncio.subprocess.PIPE,
        )

        state = StreamState(
            process=process,
            status=StreamStatus.STARTING,
            started_at=datetime.now(UTC).isoformat(),
        )
        self._streams[process_type] = state

        state._monitor_task = asyncio.create_task(
            self._monitor_process(process_type)
        )

        return state

    async def stop_stream(self, process_type: str) -> None:
        state = self._streams.pop(process_type, None)
        if not state:
            return

        if state._monitor_task and not state._monitor_task.done():
            state._monitor_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await state._monitor_task

        if state.process and state.process.returncode is None:
            state.process.terminate()
            try:
                await asyncio.wait_for(state.process.wait(), timeout=5.0)
            except TimeoutError:
                state.process.kill()
                await state.process.wait()

        stream_dir = self.base_dir / process_type
        if stream_dir.exists():
            shutil.rmtree(stream_dir, ignore_errors=True)

    async def stop_all(self) -> None:
        for pt in list(self._streams.keys()):
            await self.stop_stream(pt)

    async def _monitor_process(self, process_type: str) -> None:
        state = self._streams.get(process_type)
        if not state or not state.process or not state.process.stderr:
            return

        streaming_pattern = re.compile(rb"frame=\s*\d+.*fps=")

        try:
            while True:
                line = await state.process.stderr.readline()
                if not line:
                    break

                if state.status == StreamStatus.STARTING and streaming_pattern.search(line):
                    state.status = StreamStatus.STREAMING

            returncode = await state.process.wait()
            if process_type in self._streams:
                if returncode != 0 and state.status != StreamStatus.OFFLINE:
                    state.status = StreamStatus.ERROR
                    state.error = f"ffmpeg exited with code {returncode}"
                else:
                    state.status = StreamStatus.OFFLINE
        except asyncio.CancelledError:
            return

    def get_stream_dir(self, process_type: str) -> Path:
        return self.base_dir / process_type

    @staticmethod
    def validate_segment_name(segment: str) -> bool:
        return bool(re.match(r"^seg\d{3}\.ts$", segment))
