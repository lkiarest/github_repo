import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';

class VoiceService {
  final stt.SpeechToText _stt = stt.SpeechToText();
  final FlutterTts _tts = FlutterTts();

  bool initialized = false;

  Future<void> init() async {
    initialized = await _stt.initialize();
    await _tts.setLanguage("zh-CN");
    await _tts.setSpeechRate(0.5);
  }

  Future<String> listenOnce() async {
    String result = '';

    await _stt.listen(
      onResult: (res) {
        result = res.recognizedWords;
      },
      localeId: "zh_CN",
    );

    await Future.delayed(const Duration(seconds: 3));
    await _stt.stop();

    return result;
  }

  Future<void> speak(String text) async {
    await _tts.speak(text);
  }
}
