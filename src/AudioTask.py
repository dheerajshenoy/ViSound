from PyQt6.QtCore import QObject, pyqtSignal, QThreadPool, QRunnable
import sounddevice as sd
import numpy as np

class AudioTask(QRunnable):
    def __init__(self, audio: np.ndarray, samplerate: float, play: bool = True):
        super().__init__()
        self.audio = audio
        self.samplerate = samplerate
        self.play = play

    def run(self):
        if self.play:
            sd.play(self.audio, self.samplerate)
            sd.wait()
        else:
            sd.stop()
