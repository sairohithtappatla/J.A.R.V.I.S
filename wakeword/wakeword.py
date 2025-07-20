import pvporcupine
import pyaudio
import struct
import os
import time
import threading


class WakeWordDetector:
    def __init__(self, access_key, keyword_path, on_detect,  sensitivities, device_index=None):
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.on_detect = on_detect
        self.device_index = device_index
        self.sensitivities = sensitivities

        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=[self.keyword_path],
            keywords=["jarvis"],
            sensitivities=[0.8]  # Changed from [0.8, 0.75] to match single keyword
        )
        self.pa = pyaudio.PyAudio()

        # Automatically use default mic if device_index is None
        if self.device_index is None:
            self.device_index = self.pa.get_default_input_device_info()["index"]

        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.porcupine.frame_length
        )

        self.cooldown = False

    def listen(self):
        print("🎙️ Listening for 'Hey Jarvis' wake word...")

        try:
            while True:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm_unpacked = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                result = self.porcupine.process(pcm_unpacked)

                if result >= 0 and not self.cooldown:
                    print("✅ Wake word detected!")
                    self.cooldown = True
                    threading.Thread(target=self.on_detect).start()
                    threading.Timer(2, self.reset_cooldown).start()

        except KeyboardInterrupt:
            print("🛑 Wake word listener stopped.")
        finally:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.pa.terminate()
            self.porcupine.delete()

    def reset_cooldown(self):
        self.cooldown = False
