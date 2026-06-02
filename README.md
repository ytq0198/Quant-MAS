# Quant MAS

Quant MAS is a research project for a multi-agent quantitative research and trading platform.

The first phase focuses on a deterministic quant research loop:

1. Load data
2. Build features
3. Run strategies
4. Backtest
5. Check risk
6. Record experiments and reports

LLM agents are planned for research, planning, explanation, reporting, and tool orchestration. They must not place live orders directly.

## Development

```powershell
pip install -e .
python -m pytest -v
python -c "import quant_mas"
```

## Server

Recommended path: `/mnt/localDisk3/weizian/Quant-MAS`

Copy the server storage example and edit paths:

```bash
cp configs/storage.server.yaml.example configs/storage.server.yaml
```

Set up a Python 3.11 conda environment:

```bash
bash server/setup_server.sh
conda activate quant-mas   # required — do not use system Python 3.9
pip install -r requirements.txt
pip install -e .
```

Run tests (**always use `python -m pytest` and `python -m pip`, not bare `pip`**):

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pip install -r requirements-data.txt
python -m pip install -r requirements-ml.txt
python -m pytest -v
```

Verify the active interpreter (both must be 3.11):

```bash
which python
python --version
python -m pip --version    # must NOT show python 3.9
```

Run a small pipeline example:

```bash
bash server/run_small_pipeline.sh
```

The setup script does not download large data. The small pipeline script uses `AAPL MSFT SPY` by default and writes logs/reports to configured server paths.

## Project Principles

- Quant Engine owns deterministic computation: data, features, models, strategy, backtest, risk, and execution.
- Agent Layer owns research, planning, explanation, reporting, and orchestration.
- All trading signals must pass backtesting, risk checks, audit, and human confirmation before any live action.
- Tests must not rely on real network requests or real LLM APIs.
