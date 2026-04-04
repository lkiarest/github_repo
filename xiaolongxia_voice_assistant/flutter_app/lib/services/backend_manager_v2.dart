import 'package:shared_preferences/shared_preferences.dart';
import '../models/backend_mode.dart';

class BackendManagerV2 {
  static const _key = 'backend_mode';

  BackendMode current = BackendMode.localOpenClaw;

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final value = prefs.getString(_key);
    switch (value) {
      case 'openrouter_cloud':
        current = BackendMode.openRouterCloud;
        break;
      case 'gemini_cloud':
        current = BackendMode.geminiCloud;
        break;
      case 'local_openclaw':
      default:
        current = BackendMode.localOpenClaw;
        break;
    }
  }

  Future<void> setMode(BackendMode mode) async {
    current = mode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, mode.key);
  }
}
