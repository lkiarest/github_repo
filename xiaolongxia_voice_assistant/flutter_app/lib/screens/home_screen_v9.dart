import 'package:flutter/material.dart';
import '../services/voice_service.dart';
import 'home_screen_v8.dart';

class HomeScreenV9 extends StatefulWidget {
  const HomeScreenV9({super.key});

  @override
  State<HomeScreenV9> createState() => _HomeScreenV9State();
}

class _HomeScreenV9State extends State<HomeScreenV9> {
  final voice = VoiceService();

  @override
  void initState() {
    super.initState();
    voice.init();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        const HomeScreenV8(),
        Positioned(
          bottom: 30,
          right: 20,
          child: FloatingActionButton(
            onPressed: () async {
              final text = await voice.listenOnce();
              if (text.isNotEmpty) {
                await voice.speak(text);
              }
            },
            child: const Icon(Icons.mic),
          ),
        )
      ],
    );
  }
}
