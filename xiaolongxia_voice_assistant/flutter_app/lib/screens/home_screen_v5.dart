import 'package:flutter/material.dart';
import '../models/backend_mode.dart';
import '../services/backend_manager.dart';
import '../services/api_key_manager.dart';
import '../services/cloud_chat_service.dart';
import '../services/app_prefs.dart';

class HomeScreenV5 extends StatefulWidget {
  const HomeScreenV5({super.key});

  @override
  State<HomeScreenV5> createState() => _HomeScreenV5State();
}

class _HomeScreenV5State extends State<HomeScreenV5> {
  final backend = BackendManager();
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

  void openSettings() {
    showModalBottomSheet(
      context: context,
      builder: (_) => Column(
        children: [
          ListTile(title: const Text('切换模式')),
          ...BackendMode.values.map((m) => ListTile(
                title: Text(m.label),
                onTap: () async {
                  await backend.setMode(m);
                  setState(() => mode = m);
                  Navigator.pop(context);
                },
              )),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(actions: [IconButton(onPressed: openSettings, icon: const Icon(Icons.settings))]),
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
