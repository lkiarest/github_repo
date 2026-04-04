import 'package:shared_preferences/shared_preferences.dart';
import '../models/backend_mode.dart';

class AppPrefs {
  static const _onboardingDoneKey = 'onboarding_done';
  static const _openRouterModelKey = 'openrouter_model';
  static const _geminiModelKey = 'gemini_model';
  static const _serverUrlKey = 'local_server_url';

  Future<bool> isOnboardingDone() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_onboardingDoneKey) ?? false;
  }

  Future<void> setOnboardingDone(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_onboardingDoneKey, value);
  }

  Future<String> getModel(BackendMode mode) async {
    final prefs = await SharedPreferences.getInstance();
    switch (mode) {
      case BackendMode.openRouterCloud:
        return prefs.getString(_openRouterModelKey) ?? 'openrouter/free';
      case BackendMode.geminiCloud:
        return prefs.getString(_geminiModelKey) ?? 'gemini-2.5-flash-lite';
      case BackendMode.localOpenClaw:
        return 'local-openclaw';
    }
  }

  Future<void> setModel(BackendMode mode, String value) async {
    final prefs = await SharedPreferences.getInstance();
    switch (mode) {
      case BackendMode.openRouterCloud:
        await prefs.setString(_openRouterModelKey, value);
        break;
      case BackendMode.geminiCloud:
        await prefs.setString(_geminiModelKey, value);
        break;
      case BackendMode.localOpenClaw:
        break;
    }
  }

  Future<String> getServerUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_serverUrlKey) ?? 'http://127.0.0.1:8000';
  }

  Future<void> setServerUrl(String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_serverUrlKey, value.trim());
  }
}
