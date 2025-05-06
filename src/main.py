import os
import cv2
import matplotlib.pyplot as plt
import sounddevice as sd
import numpy as np
from GUI import MainWindow
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThreadPool
from AudioTask import AudioTask

DPC = 0.1 # duration per column in seconds
SR = 44100

image = cv2.imread("dot.png", cv2.IMREAD_GRAYSCALE)
image = cv2.resize(image, (256, 256))

def pixel_to_freq(y: float, height: float) -> float:
    return 200 + (1 - y / height) * 1800

def sonify(image: np.ndarray) -> np.ndarray:
    height, width = image.shape
    sound = np.zeros(int(width * DPC * SR))
    t_col = np.linspace(0, DPC, int(DPC * SR), endpoint=False)

    for x in range(width):
        column = image[:, x]
        column_sound = np.zeros_like(t_col)

        for y in range(height):
            intensity = column[y] / 255.0
            if intensity > 0.1:
                freq = pixel_to_freq(y, height)
                column_sound += intensity * np.sin(2 * np.pi * freq * t_col)

        start = int(x * DPC * SR)
        end = start + len(t_col)
        sound[start:end] += column_sound

    return sound

audio = sonify(image)

duration_seconds = len(audio) / SR
bar_increment_interval = duration_seconds / DPC
#print(duration_seconds / image.shape[1])

def play_pause(play: bool):
    task = AudioTask(audio, SR, play)
    GUI.threadpool.start(task)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    GUI = MainWindow()
    GUI.loadImage(image)
    GUI.dpc = DPC
    GUI.update_bar_position()

#    GUI.set_bar_timing(DPC * 2.2)
    GUI.play_pause_signal.connect(play_pause)
    app.exec()
