import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/backend_mode.dart';

class CloudChatService {
  Future<String> sendMessage({
    required BackendMode mode,
    required String message,
    required String apiKey,
    String model = 'openrouter/free',
  }) async {
    switch (mode) {
      case BackendMode.openRouterCloud:
        return _sendOpenRouter(message: message, apiKey: apiKey, model: model);
      case BackendMode.geminiCloud:
        return _sendGemini(message: message, apiKey: apiKey, model: model);
      case BackendMode.localOpenClaw:
        throw UnsupportedError('CloudChatService does not handle localOpenClaw');
    }
  }

  Future<String> _sendOpenRouter({
    required String message,
    required String apiKey,
    required String model,
  }) async {
    final res = await http.post(
      Uri.parse('https://openrouter.ai/api/v1/chat/completions'),
      headers: {
        'Authorization': 'Bearer $apiKey',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com/lkiarest/github_repo',
        'X-Title': 'XiaoLongXia Flutter',
      },
      body: jsonEncode({
        'model': model,
        'messages': [
          {'role': 'user', 'content': message}
        ],
      }),
    );

    if (res.statusCode >= 400) {
      throw Exception('OpenRouter error: ${res.body}');
    }

    final data = jsonDecode(res.body) as Map<String, dynamic>;
    return (((data['choices'] ?? []) as List).firstOrNull?['message'] ?? const {})['content']?.toString() ?? '';
  }

  Future<String> _sendGemini({
    required String message,
    required String apiKey,
    required String model,
  }) async {
    final geminiModel = model.isEmpty || model == 'openrouter/free' ? 'gemini-2.5-flash-lite' : model;
    final res = await http.post(
      Uri.parse('https://generativelanguage.googleapis.com/v1beta/models/$geminiModel:generateContent?key=$apiKey'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'contents': [
          {
            'parts': [
              {'text': message}
            ]
          }
        ]
      }),
    );

    if (res.statusCode >= 400) {
      throw Exception('Gemini error: ${res.body}');
    }

    final data = jsonDecode(res.body) as Map<String, dynamic>;
    final candidates = (data['candidates'] ?? []) as List;
    if (candidates.isEmpty) return '';
    final content = candidates.first['content'] as Map<String, dynamic>?;
    final parts = (content?['parts'] ?? []) as List;
    if (parts.isEmpty) return '';
    return parts.first['text']?.toString() ?? '';
  }
}

extension _FirstOrNull on List {
  dynamic get firstOrNull => isEmpty ? null : first;
}
