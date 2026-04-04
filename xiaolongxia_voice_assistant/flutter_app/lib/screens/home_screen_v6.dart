import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import '../models/backend_mode.dart';
import '../services/backend_manager.dart';
import '../services/api_key_manager.dart';
import '../services/cloud_chat_service.dart';
import '../services/app_prefs.dart';

class HomeScreenV6 extends StatefulWidget {
  const HomeScreenV6({super.key});

  @override
  State<HomeScreenV6> createState() => _HomeScreenV6State();
}

class _HomeScreenV6State extends State<HomeScreenV6> {
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
    await _requestPermissions();
    await backend.load();
    setState(() => mode = backend.current);
  }

  Future<void> _requestPermissions() async {
    final mic = await Permission.microphone.request();
    if (!mic.isGranted) {
      setState(() {
        text = '请允许麦克风权限，否则语音功能无法使用';
      });
    }
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
          ListTile(
            title: const Text('打开系统设置'),
            onTap: () async {
              await openAppSettings();
            },
          ),
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
            TextField(
              controller: input,
              decoration: const InputDecoration(hintText: '输入内容'),
            ),
            ElevatedButton(onPressed: send, child: const Text('发送')),
            const SizedBox(height: 20),
            Text(text),
          ],
        ),
      ),
    );
  }
}
