from PyQt6.QtWidgets import (QMainWindow, QWidget, QLabel, QGraphicsView, QPushButton,
    QVBoxLayout, QHBoxLayout, QApplication, QGraphicsScene,
    QGraphicsPixmapItem, QGraphicsLineItem)
from PyQt6.QtGui import QPixmap, QPen, QKeySequence, QShortcut, QImage
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThreadPool
import sys
import numpy as np
import cv2
import time
from core.TraversalMode import TraversalMode

class MainWindow(QMainWindow):
    reset_signal = pyqtSignal(bool)
    pause_resume_signal = pyqtSignal(bool)
    def __init__(self):
        super().__init__()

        self.playing = False
        self.paused = False
        self.start_time = 0
        self.traversal_mode = None
        self.pixmap: QPixmap = None
        self.pixmap_item: QGraphicsPixmapItem = None
        self.dpc: float = None
        self.bar_x = 0
        self.bar_increment = 1
        self.FPS = 60

        self.layout = QVBoxLayout()
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene(self.graphics_view)
        self.layout.addWidget(self.graphics_view)
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.bar = QGraphicsLineItem()
        self.bar.setPen(QPen(Qt.GlobalColor.red, 2))

        self.timer = QTimer()
        self.timer.setInterval(int(1 / self.FPS * 1000))
        self.timer.timeout.connect(self.advance_bar)

        self.handle_keybindings()
        self.show()

    def set_traversal_mode(self, mode: TraversalMode):
        self.traversal_mode = mode

    def handle_keybindings(self):
        sc_reset = QShortcut(QKeySequence("r"), self)
        sc_reset.activated.connect(self.reset_requested)

        sc_pause_resume = QShortcut(QKeySequence("space"), self)
        sc_pause_resume.activated.connect(self.pause_resume_requested)

    def pause_resume_requested(self):
        self.playing = not self.playing
        if self.playing:
            self.start_time = time.perf_counter()
            self.timer.start()
        else:
            self.timer.stop()

        self.pause_resume_signal.emit(self.playing)

    def reset_requested(self):
        self.playing = False
        self.timer.stop()
        self.reset_signal.emit(self.playing)

    def loadImage(self, img_cv: np.ndarray) -> None:
        self.graphics_scene.clear()
        self.height, self.width = img_cv.shape
        bytes_per_line = 3 * self.width
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        qimg = QImage(img_rgb.data, self.width, self.height, bytes_per_line, QImage.Format.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qimg)
        self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
        self.graphics_scene.addItem(self.pixmap_item)
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_scene.addItem(self.bar)

    def init_bar_position(self):

        match self.traversal_mode:

            case TraversalMode.LeftToRight:
                self.bar_x = 0
                self.bar.setLine(self.bar_x, 0, self.bar_x, self.height)

            case TraversalMode.RightToLeft:
                self.bar_x = self.width
                self.bar.setLine(self.bar_x, 0, self.bar_x, self.height)

    def advance_bar(self):
        elapsed = time.perf_counter() - self.start_time

        match self.traversal_mode:

            case TraversalMode.LeftToRight:
                if self.bar_x < self.pixmap.width():
                    self.bar_x = int(elapsed / self.dpc)
                    self.bar.setLine(self.bar_x, 0, self.bar_x, self.height)
                else:
                    self.playing = False
                    self.timer.stop()

            case TraversalMode.RightToLeft:
                if self.bar_x > 0:
                    self.bar_x = self.width - int(elapsed / self.dpc)
                    self.bar.setLine(self.bar_x, 0, self.bar_x, self.height)
                else:
                    self.playing = False
                    self.timer.stop()
