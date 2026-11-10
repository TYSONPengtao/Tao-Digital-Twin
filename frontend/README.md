# 家庭数字孪生 Web 演示

React 与 Three.js 显示模拟设备，FastAPI 提供模拟状态。浏览器先请求 `/api/devices`，再用 `/ws/telemetry` 接收遥测。住宅几何、UE5 场景与本地软件灯的进度见 [智慧家逐版台账](../docs/history/smart-home.md)。

## 本地运行

在仓库根目录为后端准备 Python 环境，安装依赖后启动服务。

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

另开终端，从仓库根目录启动 Web 客户端。

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev
```

用 Vite 输出的本地地址打开页面。开发时可运行 `npm --prefix frontend run lint` 与 `npm --prefix frontend run build`。
