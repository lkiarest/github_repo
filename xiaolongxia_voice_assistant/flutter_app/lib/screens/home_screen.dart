import 'package:flutter/material.dart';
import '../widgets/voice_orb.dart';
import '../services/realtime_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final realtime = RealtimeService();
  String text = "准备中...";

  @override
  void initState() {
    super.initState();
    init();
  }

  Future<void> init() async {
    await realtime.connect();

    realtime.onText = (t) {
      setState(() {
        text = t;
      });
    };

    realtime.onAudio = (bytes) async {
      await realtime.playAudio(bytes);
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const SizedBox(height: 80),
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
