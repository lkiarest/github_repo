enum BackendMode {
  localOpenClaw,
  openRouterCloud,
  geminiCloud,
}

extension BackendModeX on BackendMode {
  String get label {
    switch (this) {
      case BackendMode.localOpenClaw:
        return '局域网 OpenClaw';
      case BackendMode.openRouterCloud:
        return 'OpenRouter 云端';
      case BackendMode.geminiCloud:
        return 'Gemini 云端';
    }
  }

  String get key {
    switch (this) {
      case BackendMode.localOpenClaw:
        return 'local_openclaw';
      case BackendMode.openRouterCloud:
        return 'openrouter_cloud';
      case BackendMode.geminiCloud:
        return 'gemini_cloud';
    }
  }

  static BackendMode fromKey(String? value) {
    for (final mode in BackendMode.values) {
      if (mode.key == value) return mode;
    }
    return BackendMode.localOpenClaw;
  }
}
