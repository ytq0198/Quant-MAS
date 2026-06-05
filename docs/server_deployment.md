# Quant MAS v5 Server Deployment / 服务器部署

This document describes the lightweight server deployment path for Quant MAS v5.

本文档说明 Quant MAS v5 的轻量服务器部署路径。

---

## Recommended Layout / 推荐目录

```text
/opt/quant-mas/
|-- repo/
|-- data/
|-- outputs/
|-- logs/
`-- .env
```

Keep `.env`, logs, and private outputs outside public static hosting.

请勿把 `.env`、logs 和私有 outputs 暴露到前端静态托管目录。

---

## Backend / 后端

```bash
export QUANT_MAS_AUTH_MODE=api_key
export QUANT_MAS_AUDIT_WRITE_PATH=/opt/quant-mas/logs/backend_audit.jsonl
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

---

## Frontend / 前端

```bash
cd frontend
npm install
npm run build
```

Serve `frontend/dist` with Nginx or Caddy.

使用 Nginx 或 Caddy 托管 `frontend/dist`。

---

## Smoke / 冒烟测试

```bash
python -m pytest tests/test_backend_status.py tests/test_backend_api.py -q
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/config/effective
```
