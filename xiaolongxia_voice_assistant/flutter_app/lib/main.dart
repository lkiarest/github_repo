import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const XiaoLongXiaApp());
}

class XiaoLongXiaApp extends StatelessWidget {
  const XiaoLongXiaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: '小龙虾语音助手',
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0B1020),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF10A37F),
          secondary: Color(0xFF34D399),
          surface: Color(0xFF111827),
        ),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
