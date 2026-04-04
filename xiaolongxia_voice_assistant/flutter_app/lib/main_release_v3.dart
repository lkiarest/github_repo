import 'package:flutter/material.dart';
import 'screens/onboarding_screen.dart';
import 'screens/home_screen_v5.dart';
import 'services/app_prefs.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = AppPrefs();
  final done = await prefs.isOnboardingDone();

  runApp(XiaoLongXiaApp(done: done));
}

class XiaoLongXiaApp extends StatelessWidget {
  final bool done;
  const XiaoLongXiaApp({super.key, required this.done});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      routes: {
        '/home': (_) => const HomeScreenV5(),
      },
      home: done ? const HomeScreenV5() : const OnboardingScreen(),
    );
  }
}
