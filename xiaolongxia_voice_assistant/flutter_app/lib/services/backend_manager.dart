import 'package:shared_preferences/shared_preferences.dart';
import '../models/backend_mode.dart';

class BackendManager {
  static const _key = 'backend_mode';

  BackendMode current = BackendMode.localOpenClaw;

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    current = BackendMode.fromKey(prefs.getString(_key));
  }

  Future<void> setMode(BackendMode mode) async {
    current = mode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, mode.key);
  }
}
