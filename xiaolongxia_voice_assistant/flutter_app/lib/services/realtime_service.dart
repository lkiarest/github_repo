import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:http/http.dart' as http;

class RealtimeService {
  RTCPeerConnection? pc;
  RTCDataChannel? dc;

  Function(String text)? onText;
  Function(Uint8List audio)? onAudio;

  final server = "http://127.0.0.1:8000";

  Future<void> connect() async {
    pc = await createPeerConnection({});

    dc = await pc!.createDataChannel("chat", RTCDataChannelInit());

    dc!.onMessage = (msg) {
      final data = jsonDecode(msg.text);

      if (data["type"] == "response.text.delta") {
        onText?.call(data["delta"]);
      }

      if (data["type"] == "response.audio.chunk") {
        final bytes = base64Decode(data["audio_base64"]);
        onAudio?.call(bytes);
      }
    };

    final stream = await navigator.mediaDevices.getUserMedia({"audio": true});
    for (var track in stream.getTracks()) {
      pc!.addTrack(track, stream);
    }

    final offer = await pc!.createOffer();
    await pc!.setLocalDescription(offer);

    final res = await http.post(
      Uri.parse("$server/rtc/offer"),
      body: jsonEncode({"sdp": offer.sdp, "type": offer.type}),
    );

    final answer = jsonDecode(res.body);
    await pc!.setRemoteDescription(RTCSessionDescription(answer["sdp"], answer["type"]));
  }

  Future<void> playAudio(Uint8List bytes) async {
    // TODO: 接入播放器（audioplayers）
  }
}
