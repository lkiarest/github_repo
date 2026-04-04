import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/backend_mode.dart';

class ApiKeyManager {
  static const _storage = FlutterSecureStorage();

  static String _keyForMode(BackendMode mode) {
    switch (mode) {
      case BackendMode.localOpenClaw:
        return 'api_key_local_openclaw';
      case BackendMode.openRouterCloud:
        return 'api_key_openrouter';
      case BackendMode.geminiCloud:
        return 'api_key_gemini';
    }
  }

  Future<String?> read(BackendMode mode) async {
    return _storage.read(key: _keyForMode(mode));
  }

  Future<void> write(BackendMode mode, String value) async {
    await _storage.write(key: _keyForMode(mode), value: value.trim());
  }

  Future<void> delete(BackendMode mode) async {
    await _storage.delete(key: _keyForMode(mode));
  }

  Future<bool> hasKey(BackendMode mode) async {
    final value = await read(mode);
    return value != null && value.trim().isNotEmpty;
  }
}
