import 'package:flutter/material.dart';
import 'screens/home_screen_v4.dart';

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
      theme: ThemeData.dark(),
      home: const HomeScreenV4(),
    );
  }
}
