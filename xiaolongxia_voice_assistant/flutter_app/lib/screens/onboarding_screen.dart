import 'package:flutter/material.dart';
import '../models/backend_mode.dart';
import '../services/app_prefs.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  BackendMode mode = BackendMode.openRouterCloud;
  final prefs = AppPrefs();

  void finish() async {
    await prefs.setOnboardingDone(true);
    if (!mounted) return;
    Navigator.pushReplacementNamed(context, '/home');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('欢迎使用小龙虾语音助手', style: TextStyle(fontSize: 22)),
            const SizedBox(height: 30),
            const Text('选择默认模式'),
            const SizedBox(height: 20),
            DropdownButton<BackendMode>(
              value: mode,
              items: BackendMode.values
                  .map((m) => DropdownMenuItem(value: m, child: Text(m.label)))
                  .toList(),
              onChanged: (m) => setState(() => mode = m!),
            ),
            const SizedBox(height: 30),
            ElevatedButton(onPressed: finish, child: const Text('开始使用'))
          ],
        ),
      ),
    );
  }
}
