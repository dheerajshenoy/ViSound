import numpy as np
from typing import Optional, Tuple
import cv2
from visound.core.TraversalMode import TraversalMode
import soundfile as sf
import os

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
            raise FileNotFoundError(f"Image file not found or unreadable: {self._file_path}")
        self._image = cv2.resize(self._image, self._dim)

    @property
    def image(self) -> np.ndarray:
        return self._image

    def save(self, path: str) -> None:
        sf.write(path, self._audio, self._SR)

    def pixel_to_freq(self, y: float, x: int, image: np.ndarray, **kwargs) -> float:
        """
        Mapping function of pixel to frequency
        """
        return 500 + (1 - y / height) * 1800

    def LTR(self) -> np.ndarray:
        """
        Left to Right traversal of image
        """
        if self._image is None:
            raise ValueError("No image loaded to sonify.")

        self._traversal_mode = TraversalMode.LeftToRight

        sound = np.zeros(int(self._width * self._DPC * self._SR))
        t_col = np.linspace(0, self._DPC, int(self._DPC * self._SR), endpoint=False)

        for x in range(self._width):
            column = self._image[:, x]
            column_sound = np.zeros_like(t_col)

            for y in range(self._height):
                intensity = column[y] / 255.0
                if intensity > 0.1:
                    freq = self.pixel_to_freq(y, self._height)
                    column_sound += intensity * np.sin(2 * np.pi * freq * t_col)

            start = int(x * self._DPC * self._SR)
            end = start + len(t_col)
            sound[start:end] += column_sound

        self._audio = sound

        return sound

    def RTL(self) -> np.ndarray:
        """
        Right to Left traversal of image
        """

        if self._image is None:
            raise ValueError("No image loaded to sonify.")

        self._traversal_mode = TraversalMode.RightToLeft

        sound = np.zeros(int(self._width * self._DPC * self._SR))
        t_col = np.linspace(0, self._DPC, int(self._DPC * self._SR), endpoint=False)

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

        # self.audio_controller.set_params(sound, self.SR)

        return sound
