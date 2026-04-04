# XiaoLongXia Mac App

这是小龙虾本地语音助手的 macOS 图形界面外壳，推荐路线：

- 前端：React + Vite
- 桌面封装：Tauri 2
- 后端：复用现有 Python 语音引擎

## 目标能力

- 一键启动/停止语音助手
- 查看实时状态（待唤醒 / 监听中 / 思考中 / 播放中）
- 显示最近对话
- 设置页：OpenClaw、Whisper、Piper、Porcupine 路径和开关
- 菜单栏常驻

## 目录

- `frontend/`: React UI
- `tauri/`: Tauri 宿主配置

## 建议启动方式

1. UI 启动后拉起 Python 后台进程
2. Python 将状态和日志通过本地 HTTP/WebSocket 提供给 UI
3. UI 负责展示与控制，不直接承载语音逻辑

## 下一步

- 补 Python 控制面板 API
- 将当前 V9/V10/V11 中选一个作为默认引擎
- 增加对话历史持久化
