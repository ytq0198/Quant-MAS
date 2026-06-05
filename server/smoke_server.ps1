$ErrorActionPreference = "Stop"
python -m pytest tests/test_backend_status.py tests/test_backend_api.py -q
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:8000/api/config/effective
