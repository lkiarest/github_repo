import 'package:flutter/material.dart';
import '../widgets/voice_orb.dart';
import '../services/realtime_service.dart';
import '../services/backend_manager.dart';
import '../widgets/backend_switcher.dart';
import '../models/backend_mode.dart';

class HomeScreenV2 extends StatefulWidget {
  const HomeScreenV2({super.key});

  @override
  State<HomeScreenV2> createState() => _HomeScreenV2State();
}

class _HomeScreenV2State extends State<HomeScreenV2> {
  final realtime = RealtimeService();
  final backend = BackendManager();

  String text = "准备中...";
  BackendMode mode = BackendMode.localOpenClaw;

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

      realtime.onText = (t) {
        setState(() {
          text = t;
        });
      };
    } else {
      setState(() {
        text = "当前为云端模式（文本）";
      });
    }
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
          const SizedBox(height: 40),
          const VoiceOrb(),
          const SizedBox(height: 40),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Text(
              text,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16, color: Colors.white70),
            ),
          ),
        ],
      ),
    );
  }
}
