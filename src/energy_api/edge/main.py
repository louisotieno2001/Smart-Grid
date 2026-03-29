# Author: Jerry Onyango
# Contribution: Boots the edge runtime service, wires dependencies, and manages signal-driven shutdown.

from __future__ import annotations

import logging
import signal
from types import FrameType

from energy_api.core import configure_logging

from .cloud_client import EdgeCloudClient
from .commands import CommandExecutor
from .config import EdgeServiceSettings
from .modbus_adapter import ModbusAdapter
from .poller import EdgePoller
from .replay import ReplayService
from .runtime import EdgeRuntime
from .storage.sqlite import EdgeSQLiteStore
from .supervisor import EdgeRuntimeSupervisor


def run() -> None:
    settings = EdgeServiceSettings.from_env()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    configure_logging(level=log_level)
    logger = logging.getLogger("energy_api.edge.main")

    store = EdgeSQLiteStore(settings.sqlite_path)
    adapter = ModbusAdapter(
        host=settings.modbus_host,
        port=settings.modbus_port,
        timeout_seconds=settings.modbus_timeout_seconds,
    )
    poller = EdgePoller(
        adapter=adapter,
        mappings=settings.point_mappings,
        polling_interval_seconds=settings.poll_interval_seconds,
        unit_id=settings.modbus_unit_id,
    )
    command_executor = CommandExecutor(adapter=adapter, unit_id=settings.modbus_unit_id)

    cloud = EdgeCloudClient(
        base_url=settings.api_base_url,
        timeout_seconds=settings.api_timeout_seconds,
        bearer_token=settings.api_bearer_token,
    )
    replay = ReplayService(
        store=store,
        upload_fn=lambda site_id, payload: cloud.upload_record(site_id=site_id, gateway_id=settings.gateway_id, payload=payload),
        base_backoff_seconds=settings.replay_base_backoff_seconds,
        max_backoff_seconds=settings.replay_max_backoff_seconds,
    )

    def reconcile_fn(command: dict) -> str:
        try:
            ok, _detail = command_executor.reconcile_only(command.get("payload", {}))
            return "acked" if ok else "failed"
        except Exception:
            return "failed"

    runtime = EdgeRuntime(
        store=store,
        replay=replay,
        poller=poller,
        command_executor=command_executor,
        site_id=settings.site_id,
        command_reconcile_fn=reconcile_fn,
    )
    supervisor = EdgeRuntimeSupervisor(runtime=runtime, settings=settings)

    def _handle_signal(signum: int, _frame: FrameType | None) -> None:
        logger.info("edge_signal_received signum=%s", signum)
        supervisor.shutdown()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    try:
        try:
            adapter.connect()
            logger.info("edge_modbus_connected host=%s port=%s", settings.modbus_host, settings.modbus_port)
        except Exception as exc:
            logger.warning("edge_modbus_connect_failed host=%s port=%s error=%s", settings.modbus_host, settings.modbus_port, exc)

        supervisor.run_forever()
    finally:
        cloud.close()
        try:
            adapter.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    run()
