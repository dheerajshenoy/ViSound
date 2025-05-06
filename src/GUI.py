from PyQt6.QtWidgets import (QMainWindow, QWidget, QLabel, QGraphicsView, QPushButton,
                             QVBoxLayout, QHBoxLayout, QApplication, QGraphicsScene,
                             QGraphicsPixmapItem, QGraphicsLineItem)
from PyQt6.QtGui import QPixmap, QPen, QKeySequence, QShortcut, QImage
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThreadPool
import sys
import numpy as np
import cv2
import time

class MainWindow(QMainWindow):
    play_pause_signal = pyqtSignal(bool)
    def __init__(self, interval: float = 10):
        super().__init__()

        self.threadpool = QThreadPool()
        self.playing = False
        self.layout = QVBoxLayout()
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene(self.graphics_view)
        self.layout.addWidget(self.graphics_view)
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.pixmap: QPixmap = None
        self.pixmap_item: QGraphicsPixmapItem = None
        self.dpc: float = None

        self.bar_x = 0
        self.bar_increment = 1
        self.bar = QGraphicsLineItem()
        self.bar.setPen(QPen(Qt.GlobalColor.red, 2))

        self.timer = QTimer()
        self.timer.setInterval(60)
        self.timer.timeout.connect(self.advance_bar)

        self.handle_keybindings()
        self.show()

    def handle_keybindings(self):
        sc_play_pause = QShortcut(QKeySequence("p"), self)
        sc_play_pause.activated.connect(self.play_pause_requested)

    def play_pause_requested(self):
        self.playing = not self.playing

        if self.playing:
            self.start_time = time.perf_counter()
            self.timer.start()
        else:
            self.timer.stop()
        self.play_pause_signal.emit(self.playing)

    # def loadImage(self, path: str) -> None:
    #     self.pixmap = QPixmap(path)
    #     self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
    #     self.graphics_scene.addItem(self.pixmap_item)
    #     self.graphics_view.setScene(self.graphics_scene)
    def loadImage(self, img_cv: np.ndarray) -> None:
        height, width = img_cv.shape
        bytes_per_line = 3 * width
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        qimg = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qimg)
        self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
        self.graphics_scene.addItem(self.pixmap_item)
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_scene.addItem(self.bar)


    def update_bar_position(self):
        height = self.pixmap.height()
        self.bar.setLine(self.bar_x, 0, self.bar_x, height)

    def advance_bar(self):
        elapsed = time.perf_counter() - self.start_time
        self.bar_x = int(elapsed / self.dpc)
        if self.bar_x < self.pixmap.width():
#            self.bar_x += self.bar_increment
            self.update_bar_position()
        else:
            self.timer.stop()

    def closeEvent(self, event):
        self.threadpool.clear()
        self.threadpool.waitForDone()
        event.accept()

    def set_bar_timing(self, dpc: float):
        self.bar_increment_interval = int(dpc * 1000)
        self.timer.setInterval(self.bar_increment_interval)
