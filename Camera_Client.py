from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
import imagezmq
import pyqtgraph as pg


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        # self.image_hub = imagezmq.ImageHub()
        self.image_hub = imagezmq.ImageHub(open_port='tcp://164.54.162.106:5555', REQ_REP=False)

    def run(self):
        # capture from web cam
        while self._run_flag:
            rpi_name, image = self.image_hub.recv_image()
            # self.image_hub.send_reply(b'OK')
            if rpi_name=='chemmat-pi106':
                self.change_pixmap_signal.emit(image)
        # shut down capture system


    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
        self.image_hub.close()


class Camera_Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Widget")
        self.disply_width = 1920
        self.display_height = 720
        # create the label that holds the image
        self.image_item = pg.ImageView(parent=self,view=pg.PlotItem())
        self.image_item.getHistogramWidget().disableAutoHistogramRange()
        #self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('Webcam')

        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_item)
        vbox.addWidget(self.textLabel)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        #qt_img = self.convert_cv_qt(cv_img)
        #self.image_label.setPixmap(qt_img)
        self.image_item.setImage(cv_img.T,autoHistogramRange=False,autoLevels=False)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = Camera_Widget()
    a.show()
    sys.exit(app.exec_())