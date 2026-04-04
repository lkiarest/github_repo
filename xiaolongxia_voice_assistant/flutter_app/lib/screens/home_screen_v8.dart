import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';

import '../models/backend_mode.dart';
import '../services/api_key_manager.dart';
import '../services/app_prefs.dart';
import '../services/backend_manager_v2.dart';
import '../services/cloud_chat_service.dart';
import '../widgets/api_key_dialog.dart';
import '../widgets/backend_switcher.dart';

class HomeScreenV8 extends StatefulWidget {
  const HomeScreenV8({super.key});

  @override
  State<HomeScreenV8> createState() => _HomeScreenV8State();
}

class _HomeScreenV8State extends State<HomeScreenV8> {
  final backendManager = BackendManagerV2();
  final apiKeyManager = ApiKeyManager();
  final cloud = CloudChatService();
  final prefs = AppPrefs();

  BackendMode mode = BackendMode.openRouterCloud;
  final inputController = TextEditingController();
  String statusText = '初始化中...';
  bool sending = false;
  String currentModel = 'openrouter/free';
  String localServerUrl = 'http://127.0.0.1:8000';
  bool hasApiKey = false;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    await Permission.microphone.request();
    await backendManager.load();
    mode = backendManager.current;
    currentModel = await prefs.getModel(mode);
    localServerUrl = await prefs.getServerUrl();
    hasApiKey = await apiKeyManager.hasKey(mode);

    setState(() {
      statusText = _buildReadyText();
    });
  }

  String _buildReadyText() {
    switch (mode) {
      case BackendMode.localOpenClaw:
        return '当前模式：局域网 OpenClaw\n服务器：$localServerUrl\n说明：本地模式需要你的局域网后端在线。';
      case BackendMode.openRouterCloud:
        return hasApiKey
            ? '当前模式：OpenRouter 云端\n模型：$currentModel\n现在可以直接输入内容测试。'
            : '当前模式：OpenRouter 云端\n模型：$currentModel\n请先点“设置 Key”。';
      case BackendMode.geminiCloud:
        return hasApiKey
            ? '当前模式：Gemini 云端\n模型：$currentModel\n现在可以直接输入内容测试。'
            : '当前模式：Gemini 云端\n模型：$currentModel\n请先点“设置 Key”。';
    }
  }

  Future<void> _switchMode(BackendMode newMode) async {
    await backendManager.setMode(newMode);
    final model = await prefs.getModel(newMode);
    final hasKey = await apiKeyManager.hasKey(newMode);

    setState(() {
      mode = newMode;
      currentModel = model;
      hasApiKey = hasKey;
      statusText = _buildReadyText();
    });
  }

  Future<void> _setApiKey() async {
    if (mode == BackendMode.localOpenClaw) {
      setState(() {
        statusText = '本地模式不需要云端 API Key。';
      });
      return;
    }

    final key = await showApiKeyDialog(context, '设置 ${mode.label} Key');
    if (key == null || key.trim().isEmpty) {
      return;
    }

    await apiKeyManager.write(mode, key);
    final hasKey = await apiKeyManager.hasKey(mode);
    setState(() {
      hasApiKey = hasKey;
      statusText = 'Key 已保存。\n${_buildReadyText()}';
    });
  }

  Future<void> _pickModel() async {
    final controller = TextEditingController(text: currentModel);
    final value = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('设置模型'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            hintText: '例如 openrouter/free 或 gemini-2.5-flash-lite',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, controller.text.trim()),
            child: const Text('保存'),
          ),
        ],
      ),
    );

    if (value == null || value.isEmpty) return;
    await prefs.setModel(mode, value);
    setState(() {
      currentModel = value;
      statusText = _buildReadyText();
    });
  }

  Future<void> _setLocalServerUrl() async {
    final controller = TextEditingController(text: localServerUrl);
    final value = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('设置局域网服务地址'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            hintText: '例如 http://192.168.1.10:8000',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, controller.text.trim()),
            child: const Text('保存'),
          ),
        ],
      ),
    );

    if (value == null || value.isEmpty) return;
    await prefs.setServerUrl(value);
    setState(() {
      localServerUrl = value;
      statusText = _buildReadyText();
    });
  }

  Future<void> _send() async {
    final message = inputController.text.trim();
    if (message.isEmpty) {
      setState(() {
        statusText = '请先输入内容。';
      });
      return;
    }

    if (mode == BackendMode.localOpenClaw) {
      setState(() {
        statusText = '本地模式的移动端语音链路后续接入。\n当前测试建议先切云端模式验证整体可用性。';
      });
      return;
    }

    final apiKey = await apiKeyManager.read(mode);
    if (apiKey == null || apiKey.trim().isEmpty) {
      setState(() {
        statusText = '请先设置 ${mode.label} 的 API Key。';
      });
      return;
    }

    setState(() {
      sending = true;
      statusText = '请求中...';
    });

    try {
      final reply = await cloud.sendMessage(
        mode: mode,
        message: message,
        apiKey: apiKey,
        model: currentModel,
      );
      setState(() {
        statusText = reply.isEmpty ? '已返回，但内容为空。' : reply;
      });
    } catch (e) {
      setState(() {
        statusText = '请求失败：$e';
      });
    } finally {
      setState(() {
        sending = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('小龙虾助手'),
        actions: [
          IconButton(
            onPressed: _setApiKey,
            icon: const Icon(Icons.vpn_key),
            tooltip: '设置 Key',
          ),
          IconButton(
            onPressed: _pickModel,
            icon: const Icon(Icons.tune),
            tooltip: '设置模型',
          ),
          IconButton(
            onPressed: _setLocalServerUrl,
            icon: const Icon(Icons.settings_ethernet),
            tooltip: '设置本地服务地址',
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              BackendSwitcher(current: mode, onChanged: _switchMode),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.06),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(statusText),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: inputController,
                minLines: 3,
                maxLines: 6,
                decoration: const InputDecoration(
                  hintText: '输入你想让助手处理的内容…',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: sending ? null : _send,
                child: Text(sending ? '发送中...' : '发送'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
