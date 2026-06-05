# Quant MAS v5 Release Checklist / 发布检查清单

## Local / 本地

- [ ] Targeted backend pytest passes.
- [ ] `python -m compileall src/backend` passes.
- [ ] Sensitive phrase scan passes.
- [ ] README/docs links are checked.

## Frontend / 前端

- [ ] `npm install` passes.
- [ ] `npm run build` passes.
- [ ] Dashboard opens.
- [ ] API key panel works against server backend.

## Server / 服务器

- [ ] Backend starts with `QUANT_MAS_AUTH_MODE=api_key`.
- [ ] `/api/health` returns `ok`.
- [ ] `/api/health/deep` shows backend and optional component readiness.
- [ ] `/api/metrics/summary` returns readiness metrics only.
- [ ] `/api/logs/recent` can read configured JSONL logs or return an empty safe list.
- [ ] `/api/config/effective` redacts secrets.
- [ ] Artifact APIs read server paths.
- [ ] Audit JSONL writes outside public static paths.

## Safety / 安全

- [ ] No live-trading endpoint exists.
- [ ] No broker/order path is exposed.
- [ ] Raw API keys are not logged.
- [ ] OOS and non-OOS metrics are visibly separated.
- [ ] Demo language does not contain future-return promises.
