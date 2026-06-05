# Quant MAS v4 Frontend

React + Vite dashboard for the Quant MAS v4 full-stack skeleton.

Quant MAS v4 全栈骨架的 React + Vite 仪表盘。

## Local Development / 本地开发

```bash
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

Vite 开发服务器会把 `/api` 代理到 `http://127.0.0.1:8000`。

## Backend API / 后端 API

Start the backend from the repository root:

从仓库根目录启动后端：

```bash
python -m uvicorn backend.app:app --reload
```
