# XiaoLongXia Flutter App

这是面向 **Android / iOS** 的 Flutter 版本移动端壳，目标是复用现有服务端能力：

- WebRTC / WebSocket 实时语音
- 模型切换
- 对话记录
- 跨平台 UI

## 规划架构

- Flutter 前端：麦克风权限、实时语音 UI、会话展示、设置页
- 后端：继续复用现有 `server_voice_aiortc_v3.py`、`server_v3.py`
- 通信：
  - 控制与配置：HTTP
  - 实时语音：WebRTC

## 推荐目录

- `lib/main.dart`: App 入口
- `lib/screens/home_screen.dart`: 主界面
- `lib/services/api_service.dart`: HTTP 接口
- `lib/services/realtime_service.dart`: WebRTC 信令与事件处理
- `lib/widgets/voice_orb.dart`: ChatGPT 风格语音动画

## 下一步

1. 初始化 Flutter 工程
2. 接入麦克风权限
3. 接入 WebRTC 信令
4. 接入 `/config` 和 `/status`
5. 做 Android / iOS 打包
