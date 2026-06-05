# Quant MAS v5 Server Environment / 服务器环境变量

Use this document to configure server mode.

使用本文档配置服务器模式。

```bash
export QUANT_MAS_ENV=server
export QUANT_MAS_AUTH_MODE=api_key
export QUANT_MAS_API_KEYS="viewer-key:viewer,researcher-key:researcher,reviewer-key:reviewer,admin-key:admin"
export QUANT_MAS_AUDIT_WRITE_PATH=/opt/quant-mas/logs/backend_audit.jsonl
export QUANT_MAS_LOG_ROOT=/opt/quant-mas/logs
export QUANT_MAS_ARTIFACT_ROOT=/opt/quant-mas/repo
export QUANT_MAS_EXPERIMENT_MEMORY_PATH=/opt/quant-mas/outputs/reports/experiments.json
export QUANT_MAS_PAPER_DIR=/opt/quant-mas/outputs/paper
export QUANT_MAS_AUDIT_DIR=/opt/quant-mas/outputs/pipelines
```

Never commit real API keys, tokens, DSNs, or passwords.

不要提交真实 API key、token、DSN 或密码。
