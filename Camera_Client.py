from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QSpacerItem
from PyQt5.QtGui import QPixmap
from PyQt5.Qt import QSizePolicy
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
import imagezmq
import pyqtgraph as pg
from Image_Widget import  Image_Widget
import copy


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.image_hub = imagezmq.ImageHub()
        #self.image_hub = imagezmq.ImageHub(open_port='tcp://164.54.162.106:5555', REQ_REP=False)

    def run(self):
        # capture from web cam
        while self._run_flag:
            rpi_name, image = self.image_hub.recv_image()
            self.image_hub.send_reply(b'OK')
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
        img = np.random.rand(1920, 720)
        self.image_widget=Image_Widget(img,transpose=True)
        self.pos = [[100, 100], [200, 100], [200, 200], [100, 200]]
        #self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.controlsText=QLabel('Controls')
        self.addROIPushButton=QPushButton('Add ROI')
        self.addROIPushButton.clicked.connect(self.addROI)
        self.showROICheckBox=QCheckBox('Show ROI')
        self.showROICheckBox.setEnabled(False)
        self.showROICheckBox.stateChanged.connect(self.showhideROI)
        self.removeROIPushButton=QPushButton('Remove ROI')
        self.transformCheckBox=QCheckBox('Transform')
        self.transformCheckBox.setEnabled(False)

        # create a vertical box layout and add the two labels
        hbox = QHBoxLayout()
        img_vbox = QVBoxLayout()
        img_vbox.addWidget(self.image_widget)

        control_vbox = QVBoxLayout()
        control_vbox.addWidget(self.controlsText)
        control_vbox.addWidget(self.addROIPushButton)
        control_vbox.addWidget(self.showROICheckBox)
        control_vbox.addWidget(self.removeROIPushButton)
        self.removeROIPushButton.clicked.connect(self.removeROI)
        self.removeROIPushButton.setEnabled(False)
        control_vbox.addWidget(self.transformCheckBox)
        spacer_item=QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        control_vbox.addItem(spacer_item)
        # set the vbox layout as the widgets layout
        hbox.addLayout(img_vbox)
        hbox.addLayout(control_vbox)
        self.setLayout(hbox)

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    def addROI(self):
        self.ROI=pg.PolyLineROI(self.pos,closed=True)
        self.image_widget.imageView.view.addItem(self.ROI)
        self.addROIPushButton.setEnabled(False)
        self.removeROIPushButton.setEnabled(True)
        self.showROICheckBox.setEnabled(True)
        self.showROICheckBox.setChecked(True)
        self.transformCheckBox.setEnabled(True)
        self.get_ROI_pos()
        self.ROI.sigRegionChangeFinished.connect(self.get_ROI_pos)


    def get_ROI_pos(self):
        handles=self.ROI.getHandles()
        self.ROI_pos=[]
        for handle in handles[:2]:
            self.ROI_pos.append([handle.pos().x(), handle.pos().y()])
        for handle in handles[3:1:-1]:
            self.ROI_pos.append([handle.pos().x(), handle.pos().y()])
        self.new_pos=copy.copy(self.ROI_pos)
        self.resmat=cv2.getPerspectiveTransform(np.float32(self.ROI_pos),np.float32(self.new_pos))

    def removeROI(self):
        self.pos=[]
        self.transformCheckBox.setChecked(False)
        self.transformCheckBox.setEnabled(False)
        for handle in self.ROI.getHandles():
            self.pos.append([handle.pos().x(),handle.pos().y()])
        self.showROICheckBox.setChecked(False)
        self.image_widget.imageView.view.removeItem(self.ROI)
        self.addROIPushButton.setEnabled(True)
        self.removeROIPushButton.setEnabled(False)
        self.showROICheckBox.setEnabled(False)

    def showhideROI(self):
        if self.showROICheckBox.isChecked():
            self.ROI.show()
        else:
            self.ROI.hide()


    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        #qt_img = self.convert_cv_qt(cv_img)
        #self.image_label.setPixmap(qt_img)
        if self.transformCheckBox.isChecked():
            new_img = cv2.warpPerspective(cv_img.T, self.resmat, (self.disply_width,self.display_height))
        else:
            new_img = cv_img.T
        self.image_widget.setImage(new_img,transpose=False)#,autoHistogramRange=False,autoLevels=False)

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