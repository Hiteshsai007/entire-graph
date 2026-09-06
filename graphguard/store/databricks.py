"""Upload GraphGuard report artifacts to a Unity Catalog volume."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class DatabricksIntegrationError(RuntimeError):
    """Base error for the optional Databricks integration."""


class DatabricksConfigurationError(DatabricksIntegrationError):
    """Raised when required Databricks configuration is unavailable."""


class DatabricksDependencyError(DatabricksIntegrationError):
    """Raised when the optional Databricks SDK is not installed."""


@dataclass(frozen=True)
class DatabricksConfig:
    """Workspace and Unity Catalog destination for GraphGuard artifacts."""

    host: str
    token: str
    catalog: str
    schema: str
    volume: str

    @property
    def reports_path(self) -> str:
        return f"/Volumes/{self.catalog}/{self.schema}/{self.volume}/graphguard/reports"

    @classmethod
    def from_env(cls) -> "DatabricksConfig":
        names = (
            "DATABRICKS_HOST",
            "DATABRICKS_TOKEN",
            "DATABRICKS_CATALOG",
            "DATABRICKS_SCHEMA",
            "DATABRICKS_VOLUME",
        )
        values = {name: os.environ.get(name, "").strip() for name in names}
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise DatabricksConfigurationError(
                "Databricks export is not configured. Set " + ", ".join(missing) + "."
            )
        return cls(
            host=values["DATABRICKS_HOST"],
            token=values["DATABRICKS_TOKEN"],
            catalog=values["DATABRICKS_CATALOG"],
            schema=values["DATABRICKS_SCHEMA"],
            volume=values["DATABRICKS_VOLUME"],
        )


@dataclass(frozen=True)
class DatabricksPushResult:
    """Files staged for the Databricks notebook to materialize."""

    destination: str
    uploaded_files: tuple[str, ...]


def push_to_databricks(
    data_dir: str | Path | None = None,
    config: DatabricksConfig | None = None,
    client: Any | None = None,
) -> DatabricksPushResult:
    """Upload local ``report-*.json`` artifacts to a Unity Catalog volume.

    The companion Databricks notebook owns Spark table writes and MLflow logging.
    This keeps Entire Graph and pytest on the local machine where reports originate.
    """
    config = config or DatabricksConfig.from_env()
    source_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parent.parent / "data"
    reports = tuple(sorted(source_dir.glob("report-*.json")))
    if not reports:
        raise DatabricksIntegrationError(
            f"No GraphGuard report JSON files found in {source_dir}. Run analysis first."
        )

    if client is None:
        try:
            from databricks.sdk import WorkspaceClient
        except ImportError as exc:
            raise DatabricksDependencyError(
                "Install the optional Databricks dependency with "
                '`python -m pip install -e "./graphguard[databricks]"`. '
            ) from exc
        client = WorkspaceClient(host=config.host, token=config.token)

    client.files.create_directory(config.reports_path)
    uploaded = []
    for report in reports:
        destination = f"{config.reports_path}/{report.name}"
        client.files.upload_from(destination, str(report), overwrite=True)
        uploaded.append(destination)

    return DatabricksPushResult(
        destination=config.reports_path,
        uploaded_files=tuple(uploaded),
    )
