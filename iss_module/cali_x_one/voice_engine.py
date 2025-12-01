import asyncio, threading, time, os, tempfile
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO

class VoiceEngine:
    def __init__(self):
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone()
        self._mute = False

    # ---- TTS --------------------------------------------------------------
    async def speak(self, text: str):
        if self._mute:
            print(f"[VOICE] {text}")  # Fallback when muted
            return

        try:
            # Generate TTS audio
            tts = gTTS(text)
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tts.save(tmp.name)

                # Try to play with system default player
                if os.name == 'nt':  # Windows
                    os.system(f'start /min "" "{tmp.name}"')
                else:  # Linux/Mac
                    os.system(f'xdg-open "{tmp.name}" &')

                # Clean up after a delay
                await asyncio.sleep(2)
                try:
                    os.unlink(tmp.name)
                except:
                    pass

        except Exception as e:
            print(f"[VOICE] {text} (TTS failed: {e})")

    # ---- Wake-word --------------------------------------------------------
    async def listen_for_wake(self, word: str, callback):
        def _listen():
            with self.mic as source:
                self.rec.adjust_for_ambient_noise(source)
                print(f"[VOICE] Listening for wake word: '{word}'")
                while True:
                    if self._mute:
                        time.sleep(0.5)
                        continue
                    try:
                        audio = self.rec.listen(source, timeout=0.5, phrase_time_limit=3)
                        txt = self.rec.recognize_google(audio).lower()
                        if word in txt:
                            asyncio.run(callback(txt))
                    except sr.WaitTimeoutError:
                        pass
                    except sr.UnknownValueError:
                        pass
                    except Exception as e:
                        print(f"[VOICE] Recognition error: {e}")
        threading.Thread(target=_listen, daemon=True).start()

    def mute(self):
        self._mute = not self._mute
        status = "muted" if self._mute else "unmuted"
        print(f"[VOICE] {status}")