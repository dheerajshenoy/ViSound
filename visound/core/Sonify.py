import numpy as np
from typing import Optional, Tuple
import cv2
from visound.core.TraversalMode import TraversalMode

class Sonify:
    def __init__(self,
                 file_path: str,
                 dimension: Tuple[int, int] = (128, 128),
                 duration_per_column: Optional[float] = 0.01,
                 sample_rate: Optional[float] = 44100):

        self.file_path = file_path
        self.dim = dimension
        self.DPC = duration_per_column
        self.SR = sample_rate
        self.height = self.dim[0]
        self.width = self.dim[1]
        self.traversal_mode = None

        self.image = cv2.imread(self.file_path, cv2.IMREAD_GRAYSCALE)

        if self.image is None:
            raise FileNotFoundError(f"Imafe file not found or unreadable: {self.file_path}")
        self.image = cv2.resize(self.image, self.dim)



        # from core.AudioController import AudioController
        # self.audio_controller = AudioController()

    # def GUI(self) -> None:
    #     import sys
    #     from PyQt6.QtWidgets import QApplication
    #     from core.GUI import MainWindow

    #     app = QApplication(sys.argv)
    #     GUI = MainWindow()
    #     GUI.set_traversal_mode(self.traversal_mode)
    #     GUI.loadImage(self.image)
    #     GUI.dpc = self.DPC
    #     GUI.init_bar_position()
    #     GUI.reset_signal.connect(self.reset)
    #     GUI.pause_resume_signal.connect(self.pause_or_resume)
    #     app.exec()

    # def pause_or_resume(self, pause: bool) -> None:
    #     if pause:
    #         self.audio_controller.resume()
    #     else:
    #         self.audio_controller.pause()

    # def reset(self) -> None:
    #     self.audio_controller.reset()

    def pixel_to_freq(self, y: float, height: float) -> float:
        """
        Mapping function of pixel to frequency
        """
        return 200 + (1 - y / height) * 1800

    def LTR(self) -> np.ndarray:
        """
        Left to Right traversal of image
        """
        if self.image is None:
            raise ValueError("No image loaded to sonify.")

        self.traversal_mode = TraversalMode.LeftToRight

        sound = np.zeros(int(self.width * self.DPC * self.SR))
        t_col = np.linspace(0, self.DPC, int(self.DPC * self.SR), endpoint=False)

        for x in range(self.width):
            column = self.image[:, x]
            column_sound = np.zeros_like(t_col)

            for y in range(self.height):
                intensity = column[y] / 255.0
                if intensity > 0.1:
                    freq = self.pixel_to_freq(y, self.height)
                    column_sound += intensity * np.sin(2 * np.pi * freq * t_col)

            start = int(x * self.DPC * self.SR)
            end = start + len(t_col)
            sound[start:end] += column_sound

       # self.audio_controller.set_params(sound, self.SR)

        return sound

    def RTL(self) -> np.ndarray:
        """
        Right to Left traversal of image
        """

        if self.image is None:
            raise ValueError("No image loaded to sonify.")

        self.traversal_mode = TraversalMode.RightToLeft

        sound = np.zeros(int(self.width * self.DPC * self.SR))
        t_col = np.linspace(0, self.DPC, int(self.DPC * self.SR), endpoint=False)

        for i, x in enumerate(range(self.width - 1, -1, -1)):
            column = self.image[:, x]
            column_sound = np.zeros_like(t_col)

            for y in range(self.height):
                intensity = column[y] / 255.0
                if intensity > 0.1:
                    freq = self.pixel_to_freq(y, self.height)
                    column_sound += intensity * np.sin(2 * np.pi * freq * t_col)

            start = int(i * self.DPC * self.SR)
            end = start + len(t_col)
            sound[start:end] += column_sound

        # self.audio_controller.set_params(sound, self.SR)

        return sound
