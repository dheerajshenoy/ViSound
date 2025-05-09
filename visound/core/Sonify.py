import numpy as np
from typing import Optional, Tuple
import cv2
from visound.core.TraversalMode import TraversalMode
import soundfile as sf
import os
import sys

class Sonify:

    def __init__(self,
                 file_path: str,
                 dimension: Tuple[int, int] = (128, 128),
                 duration_per_column: Optional[float] = 0.01,
                 sample_rate: Optional[float] = 44100):

        self._file_path = file_path.replace("~", os.getenv("HOME"))
        self._dim = dimension
        self._DPC = duration_per_column
        self._SR = sample_rate
        self._height = self._dim[0]
        self._width = self._dim[1]
        self._traversal_mode = None
        self._audio = None

        self._image = cv2.imread(self._file_path, cv2.IMREAD_GRAYSCALE)

        if self._image is None:
            raise FileNotFoundError("Image file not found or unreadable:{self._file_path}")
        self._image = cv2.resize(self._image, self._dim)

    def duration(self) -> float:
        """
        Duration of the audio track in seconds
        """
        return len(self._audio) / self._SR

    @property
    def audio(self) -> np.ndarray:
        """
        Get the generated audio, if there's one otherwise return None
        """
        return self._audio

    @property
    def image(self) -> np.ndarray:
        """
        Get the input image
        """
        return self._image

    def save(self, path: str) -> None:
        """
        Save the generated audio to an output file
        """
        if path != "-":
            sf.write(path, self._audio, self._SR)
        else:
            sf.write(sys.stdout.buffer, self._audio, self._SR, format='WAV')

    def pixel_to_freq(self, y: float, x: int, height: int, width: int,
                      image: np.ndarray) -> float:
        """
        Mapping function of pixel to frequency
        """
        return 500 + (1 - y / height) * 1800

    def generate_violin_tone(self, freq: float, duration: float, sample_rate: float,
                             amplitude: float = 1.0) -> np.ndarray:
        """
        Generate a violin-like tone by combining multiple harmonics
        """
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        tone = (
            1.0 * np.sin(2 * np.pi * freq * t) +
                0.5 * np.sin(2 * np.pi * 2 * freq * t) +
                0.3 * np.sin(2 * np.pi * 3 * freq * t) +
                0.15 * np.sin(2 * np.pi * 4 * freq * t) +
                0.05 * np.sin(2 * np.pi * 5 * freq * t)
        )
        return amplitude * tone / np.max(np.abs(tone))  # normalize

    def LeftToRight(self) -> np.ndarray:
        """
        Left to Right traversal of image
        """
        if self._image is None:
            raise ValueError("No image loaded to sonify.")

        self._traversal_mode = TraversalMode.LeftToRight

        sound = np.zeros(int(self._width * self._DPC * self._SR))
        t_col = np.linspace(0, self._DPC, int(self._DPC * self._SR),
                            endpoint=False)

        for x in range(self._width):
            column = self._image[:, x]
            column_sound = np.zeros_like(t_col)

            for y in range(self._height):
                intensity = column[y] / 255.0
                if intensity > 0.5:
                    freq = self.pixel_to_freq(y, x, self._height, self._width,
                                              self._image)
                    tone = intensity * np.sin(2 * np.pi * freq * t_col)
                    # tone = self.generate_violin_tone(freq, self._DPC, self._SR,
                    #                                  intensity)
                    column_sound += tone

            start = int(x * self._DPC * self._SR)
            end = start + len(t_col)
            sound[start:end] += column_sound

        self._audio = sound

        return sound

    def RightToLeft(self) -> np.ndarray:
        """
        Right to Left traversal of image
        """

        if self._image is None:
            raise ValueError("No image loaded to sonify.")

        self._traversal_mode = TraversalMode.RightToLeft

        sound = np.zeros(int(self._width * self._DPC * self._SR))
        t_col = np.linspace(0, self._DPC, int(self._DPC * self._SR),
                            endpoint=False)

        for i, x in enumerate(range(self._width - 1, -1, -1)):
            column = self._image[:, x]
            column_sound = np.zeros_like(t_col)

            for y in range(self._height):
                intensity = column[y] / 255.0
                if intensity > 0.1:
                    freq = self.pixel_to_freq(y, self._height)
                    column_sound += intensity * np.sin(2 * np.pi * freq * t_col)

            start = int(i * self._DPC * self._SR)
            end = start + len(t_col)
            sound[start:end] += column_sound

        self._audio = sound

        return sound

    def TopToBottom(self) -> np.ndarray:
        """
        Top to bottom image traversal
        """

        if self._image is None:
            raise ValueError("No image loaded to sonify.")

        self._traversal_mode = TraversalMode.TopToBottom

        sound = np.zeros(int(self._width * self._DPC * self._SR))
        t_row = np.linspace(0, self._DPC, int(self._DPC * self._SR),
                            endpoint=False)

        for y in range(self._height):
            row = self._image[y, :]
            row_sound = np.zeros_like(t_row)

            for x in range(0, self._width - 1):
                intensity = row[y] / 255.0
                if intensity > 0.1:
                    freq = self.pixel_to_freq(y, self._height)
                    row_sound += intensity * np.sin(2 * np.pi * freq * t_row)

            start = int(y * self._DPC * self._SR)
            end = start + len(t_row)
            sound[start:end] += row_sound

        self._audio = sound

        return sound


    def BottomToTop(self) -> np.ndarray:
        """
        Bottom to top image traversal
        """

        if self._image is None:
            raise ValueError("No image loaded to sonify.")

        self._traversal_mode = TraversalMode.BottomToTop

        sound = np.zeros(int(self._width * self._DPC * self._SR))
        t_row = np.linspace(0, self._DPC, int(self._DPC * self._SR),
                            endpoint=False)

        for i, y in enumerate(range(self._height - 1, -1, -1)):
            row = self._image[y, :]
            row_sound = np.zeros_like(t_row)

            for x in range(0, self._width - 1):
                intensity = row[y] / 255.0
                if intensity > 0.1:
                    freq = self.pixel_to_freq(y, self._height)
                    row_sound += intensity * np.sin(2 * np.pi * freq * t_row)

            start = int(i * self._DPC * self._SR)
            end = start + len(t_row)
            sound[start:end] += row_sound

        self._audio = sound

        return sound
