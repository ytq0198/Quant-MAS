from __future__ import annotations

from pathlib import Path

from quant_mas.utils.env import load_dotenv


def test_load_dotenv_sets_missing_keys(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("STOOQ_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text('STOOQ_API_KEY="abc123"\n# comment\nQUANT_MAS_ENV=local\n', encoding="utf-8")

    assert load_dotenv(env_file) is True
    assert __import__("os").environ["STOOQ_API_KEY"] == "abc123"
