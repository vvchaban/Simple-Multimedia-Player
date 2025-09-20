import sys
import os
import logging
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QSlider, QLabel, QListWidget, QHBoxLayout, QMessageBox
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QUrl, QTimer

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MediaPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Audio/Video Player")
        self.setGeometry(200, 200, 800, 600)

        # Video widget
        self.video_widget = QVideoWidget()

        # Media player setup
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        # Custom media list
        self.media_list = []
        self.current_index = 0

        # Controls
        self.open_btn = QPushButton("Open Files")
        self.open_btn.clicked.connect(self.open_files)

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.player.play)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.player.pause)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.player.stop)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(lambda v: self.audio_output.setVolume(v / 100.0))

        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(lambda pos: self.player.setPosition(pos))

        self.label_position = QLabel("00:00 / 00:00")

        # Playlist widget
        self.playlist_widget = QListWidget()
        self.playlist_widget.doubleClicked.connect(self.playlist_item_double_clicked)

        # Timer for updating slider
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_position)
        self.timer.start()

        # Layouts
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(QLabel("Volume"))
        control_layout.addWidget(self.volume_slider)

        position_layout = QHBoxLayout()
        position_layout.addWidget(self.position_slider)
        position_layout.addWidget(self.label_position)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.open_btn)
        layout.addLayout(control_layout)
        layout.addLayout(position_layout)
        layout.addWidget(QLabel("Playlist"))
        layout.addWidget(self.playlist_widget)

        self.setLayout(layout)

        # Signals
        self.player.durationChanged.connect(lambda d: self.position_slider.setRange(0, d))
        self.player.positionChanged.connect(self.update_position)
        self.player.errorOccurred.connect(self.on_error)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Open Media Files", "",
            "All Files (*)"
        )
        logging.info(f"Selected files: {files}")
        if files:
            self.media_list = []
            self.playlist_widget.clear()
            for file in files:
                url = QUrl.fromLocalFile(file)
                self.media_list.append(url)
                self.playlist_widget.addItem(os.path.basename(file))
                logging.debug(f"Added to playlist: {file}")
            self.current_index = 0
            if self.media_list:
                logging.info(f"Setting source to: {self.media_list[0].toLocalFile()}")
                self.player.setSource(self.media_list[0])
                self.player.play()

    def playlist_item_double_clicked(self, index):
        self.current_index = index.row()
        self.player.setSource(self.media_list[self.current_index])
        self.player.play()

    def update_position(self):
        pos = self.player.position() // 1000
        dur = self.player.duration() // 1000
        self.position_slider.setValue(self.player.position())
        self.label_position.setText(f"{pos//60:02d}:{pos%60:02d} / {dur//60:02d}:{dur%60:02d}")

    def on_error(self, error, error_string):
        logging.error(f"Media player error: {error} - {error_string}")
        QMessageBox.warning(self, "Media Error", f"Failed to play media: {error_string}")

    def on_media_status_changed(self, status):
        logging.debug(f"Media status changed: {status}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MediaPlayer()
    player.show()
    sys.exit(app.exec())
