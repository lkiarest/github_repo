import 'package:flutter/material.dart';
import 'screens/home_screen_v7.dart';

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
      home: const HomeScreenV7(),
    );
  }
}
