import subprocess

class MacOSSayTTS:
    def __init__(self, voice="Tingting"):
        self.voice = voice

    def speak(self, text: str):
        subprocess.run(["say", "-v", self.voice, text])
