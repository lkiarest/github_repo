import 'dart:typed_data';
import 'package:audioplayers/audioplayers.dart';

class AudioPlayerService {
  final AudioPlayer _player = AudioPlayer();

  Future<void> playBytes(Uint8List bytes) async {
    await _player.play(BytesSource(bytes));
  }

  Future<void> stop() async {
    await _player.stop();
  }
}
