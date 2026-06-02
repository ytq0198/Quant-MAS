from __future__ import annotations

import pandas as pd
import pytest

from quant_mas.data import DataCatalog, ParquetStorage


def test_parquet_storage_save_load_exists(tmp_path) -> None:
    storage = ParquetStorage()
    path = tmp_path / "nested" / "prices.parquet"
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "symbol": ["TEST", "TEST"],
            "close": [10.0, 10.5],
            "volume": [1000, 1200],
        }
    )

    saved_path = storage.save(frame, path)

    assert saved_path == path
    assert storage.exists(path)
    pd.testing.assert_frame_equal(storage.load(path), frame)


def test_parquet_storage_load_missing_file(tmp_path) -> None:
    storage = ParquetStorage()

    with pytest.raises(FileNotFoundError):
        storage.load(tmp_path / "missing.parquet")


def test_data_catalog_loads_yaml_and_creates_directories(tmp_path) -> None:
    config_path = tmp_path / "configs" / "storage.yaml"
    config_path.parent.mkdir()
    config_path.write_text(
        "\n".join(
            [
                "project_root: ..",
                "raw_data_dir: data/raw",
                "processed_data_dir: data/processed",
                "features_dir: data/features",
                "models_dir: models",
                "reports_dir: outputs/reports",
                "logs_dir: logs",
            ]
        ),
        encoding="utf-8",
    )

    catalog = DataCatalog.from_yaml(config_path)

    assert catalog.project_root == tmp_path.resolve()
    for directory in catalog.directories().values():
        assert directory.is_dir()
        assert directory.is_absolute()
    assert catalog.path_for("raw_data_dir", "TEST.parquet") == (
        tmp_path / "data" / "raw" / "TEST.parquet"
    ).resolve()


def test_data_catalog_accepts_absolute_paths(tmp_path) -> None:
    external_raw_dir = tmp_path / "external" / "raw"
    config_path = tmp_path / "storage.yaml"
    config_path.write_text(
        "\n".join(
            [
                f"project_root: {tmp_path.as_posix()}",
                f"raw_data_dir: {external_raw_dir.as_posix()}",
                "processed_data_dir: data/processed",
                "features_dir: data/features",
                "models_dir: models",
                "reports_dir: outputs/reports",
                "logs_dir: logs",
            ]
        ),
        encoding="utf-8",
    )

    catalog = DataCatalog.from_yaml(config_path)

    assert catalog.raw_data_dir == external_raw_dir.resolve()
    assert external_raw_dir.is_dir()


def test_data_catalog_rejects_unknown_directory_key(tmp_path) -> None:
    config_path = tmp_path / "storage.yaml"
    config_path.write_text(
        "\n".join(
            [
                "project_root: .",
                "raw_data_dir: data/raw",
                "processed_data_dir: data/processed",
                "features_dir: data/features",
                "models_dir: models",
                "reports_dir: outputs/reports",
                "logs_dir: logs",
            ]
        ),
        encoding="utf-8",
    )
    catalog = DataCatalog.from_yaml(config_path)

    with pytest.raises(KeyError):
        catalog.path_for("unknown")

