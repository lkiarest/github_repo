import 'package:flutter/material.dart';
import '../widgets/voice_orb.dart';
import '../services/realtime_service.dart';
import '../services/backend_manager.dart';
import '../services/cloud_chat_service.dart';
import '../widgets/backend_switcher.dart';
import '../models/backend_mode.dart';

class HomeScreenV3 extends StatefulWidget {
  const HomeScreenV3({super.key});

  @override
  State<HomeScreenV3> createState() => _HomeScreenV3State();
}

class _HomeScreenV3State extends State<HomeScreenV3> {
  final realtime = RealtimeService();
  final backend = BackendManager();
  final cloud = CloudChatService();

  String text = "准备中...";
  BackendMode mode = BackendMode.localOpenClaw;

  final controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    init();
  }

  Future<void> init() async {
    await backend.load();
    mode = backend.current;

    if (mode == BackendMode.localOpenClaw) {
      await realtime.connect();
      realtime.onText = (t) => setState(() => text = t);
    }
  }

  Future<void> send() async {
    final msg = controller.text;
    if (msg.isEmpty) return;

    if (mode == BackendMode.localOpenClaw) {
      setState(() => text = "语音模式中...");
      return;
    }

    final apiKey = 'YOUR_API_KEY';

    final reply = await cloud.sendMessage(
      mode: mode,
      message: msg,
      apiKey: apiKey,
    );

    setState(() => text = reply);
  }

  void switchMode(BackendMode newMode) async {
    await backend.setMode(newMode);
    setState(() {
      mode = newMode;
      text = "已切换到 ${newMode.label}";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const SizedBox(height: 60),
          BackendSwitcher(current: mode, onChanged: switchMode),
          const SizedBox(height: 20),
          TextField(
            controller: controller,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(hintText: '输入内容...'),
          ),
          ElevatedButton(onPressed: send, child: const Text('发送')),
          const SizedBox(height: 40),
          const VoiceOrb(),
          const SizedBox(height: 40),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Text(text, style: const TextStyle(color: Colors.white70)),
          ),
        ],
      ),
    );
  }
}
