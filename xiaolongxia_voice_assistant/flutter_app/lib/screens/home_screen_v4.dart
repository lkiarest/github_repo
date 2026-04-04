import 'package:flutter/material.dart';
import '../models/backend_mode.dart';
import '../services/backend_manager.dart';
import '../services/api_key_manager.dart';
import '../services/cloud_chat_service.dart';
import '../widgets/backend_switcher.dart';
import '../widgets/api_key_dialog.dart';

class HomeScreenV4 extends StatefulWidget {
  const HomeScreenV4({super.key});

  @override
  State<HomeScreenV4> createState() => _HomeScreenV4State();
}

class _HomeScreenV4State extends State<HomeScreenV4> {
  final backend = BackendManager();
  final apiKeyManager = ApiKeyManager();
  final cloud = CloudChatService();

  BackendMode mode = BackendMode.localOpenClaw;
  String text = '准备中...';
  final input = TextEditingController();

  @override
  void initState() {
    super.initState();
    init();
  }

  Future<void> init() async {
    await backend.load();
    setState(() {
      mode = backend.current;
    });
  }

  Future<void> switchMode(BackendMode m) async {
    await backend.setMode(m);
    setState(() {
      mode = m;
      text = '已切换到 ${m.label}';
    });
  }

  Future<void> setApiKey() async {
    final key = await showApiKeyDialog(context, '设置 ${mode.label} API Key');
    if (key != null && key.isNotEmpty) {
      await apiKeyManager.write(mode, key);
      setState(() {
        text = 'API Key 已保存';
      });
    }
  }

  Future<void> send() async {
    if (mode == BackendMode.localOpenClaw) {
      setState(() => text = '本地语音模式');
      return;
    }

    final key = await apiKeyManager.read(mode);
    if (key == null || key.isEmpty) {
      setState(() => text = '请先设置 API Key');
      return;
    }

    final reply = await cloud.sendMessage(
      mode: mode,
      message: input.text,
      apiKey: key,
    );

    setState(() => text = reply);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            BackendSwitcher(current: mode, onChanged: switchMode),
            const SizedBox(height: 20),
            ElevatedButton(onPressed: setApiKey, child: const Text('设置 API Key')),
            const SizedBox(height: 20),
            TextField(
              controller: input,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(hintText: '输入内容'),
            ),
            ElevatedButton(onPressed: send, child: const Text('发送')),
            const SizedBox(height: 30),
            Text(text, style: const TextStyle(color: Colors.white70)),
          ],
        ),
      ),
    );
  }
}
