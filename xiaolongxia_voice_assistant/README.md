# XiaoLongXia Voice Assistant

一个面向本地部署的智能音箱式语音助手脚手架，目标是：

- 本地语音唤醒 / 录音 / 断句
- 本地或局域网 LLM 对话
- 文本转语音播放
- 通过 QQ 官方机器人发送消息
- 后续可扩展为流式 STT / TTS

## 当前实现

这是一个可运行的架构骨架，重点是把各层职责拆清楚：

- `app/main.py`: FastAPI 服务入口
- `app/runtime/assistant.py`: 主编排器
- `app/audio/`: 音频输入与 VAD 抽象
- `app/stt/`: 语音识别适配层
- `app/tts/`: 语音合成适配层
- `app/agent/`: 意图识别与工具调用
- `app/integrations/qq_bot.py`: QQ 机器人发送消息

## 快速开始

```bash
cd xiaolongxia_voice_assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8080
```

## 环境变量

见 `.env.example`。

重点：

- `LLM_BACKEND`: `mock` / `openai_compatible`
- `OPENAI_COMPATIBLE_BASE_URL`: 你的本地模型服务地址
- `OPENAI_COMPATIBLE_API_KEY`: 如果服务需要
- `QQ_BOT_APPID`: QQ 机器人 AppID
- `QQ_BOT_TOKEN`: QQ 机器人 token
- `QQ_BOT_SECRET`: QQ 机器人 secret
- `QQ_DEFAULT_CHANNEL_OR_GROUP`: 默认投递目标

## HTTP 接口

### 1. 健康检查

```bash
curl http://127.0.0.1:8080/healthz
```

### 2. 文本对话

```bash
curl -X POST http://127.0.0.1:8080/chat \
  -H 'Content-Type: application/json' \
  -d '{"text":"给我的QQ发消息：我到家了"}'
```

### 3. 发送 QQ 消息

```bash
curl -X POST http://127.0.0.1:8080/actions/send-qq-message \
  -H 'Content-Type: application/json' \
  -d '{"content":"我到家了"}'
```

## 推荐下一步

1. 把 `MockSpeechToTextEngine` 替换成 `whisper.cpp` 流式适配器
2. 把 `MockTextToSpeechEngine` 替换成 `piper` 或你现有 TTS
3. 在 `AudioInputService` 中接入真实麦克风 + WebRTC VAD / Silero VAD
4. 按你的 QQ 机器人场景完善私聊 / 群聊目标映射
5. 增加 websocket 流式接口，实现边听边转写边播报

## 注意

- QQ 官方机器人存在会话、频控和场景限制
- 当前仓库提供的是工程骨架和关键逻辑，不包含真实 AppID / Token
- 实时语音的最终体验主要取决于音频设备、VAD 与 STT 的延迟
