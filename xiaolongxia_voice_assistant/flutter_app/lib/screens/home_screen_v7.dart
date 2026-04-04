import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import '../models/backend_mode.dart';
import '../services/backend_manager_v2.dart';
import '../services/api_key_manager.dart';
import '../services/cloud_chat_service.dart';
import '../services/app_prefs.dart';

class HomeScreenV7 extends StatefulWidget {
  const HomeScreenV7({super.key});

  @override
  State<HomeScreenV7> createState() => _HomeScreenV7State();
}

class _HomeScreenV7State extends State<HomeScreenV7> {
  final backend = BackendManagerV2();
  final apiKeyManager = ApiKeyManager();
  final cloud = CloudChatService();
  final prefs = AppPrefs();

  BackendMode mode = BackendMode.openRouterCloud;
  String text = '准备中...';
  final input = TextEditingController();

  @override
  void initState() {
    super.initState();
    init();
  }

  Future<void> init() async {
    await Permission.microphone.request();
    await backend.load();
    setState(() => mode = backend.current);
  }

  Future<void> send() async {
    final key = await apiKeyManager.read(mode);

    if (mode != BackendMode.localOpenClaw && (key == null || key.isEmpty)) {
      setState(() => text = '请先设置API Key');
      return;
    }

    final model = await prefs.getModel(mode);

    final reply = await cloud.sendMessage(
      mode: mode,
      message: input.text,
      apiKey: key ?? '',
      model: model,
    );

    setState(() => text = reply);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('小龙虾助手')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(controller: input),
            ElevatedButton(onPressed: send, child: const Text('发送')),
            const SizedBox(height: 20),
            Text(text),
          ],
        ),
      ),
    );
  }
}
