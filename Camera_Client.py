from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QSpacerItem, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.Qt import QSizePolicy, QIntValidator
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
        self.disply_width = 1290
        self.display_height = 720
        self.intValidator=QIntValidator()
        # create the label that holds the image
        img = np.random.rand(1290, 720)
        self.image_widget=Image_Widget(img,transpose=True)
        self.pos = [[0, 0], [100, 0], [100, 100], [0, 100]]
        #self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.controlsText=QLabel('Controls')
        self.addROIPushButton=QPushButton('Add ROI')
        self.addROIPushButton.clicked.connect(self.addROI)
        self.showROICheckBox=QCheckBox('Show ROI')
        self.showROICheckBox.setEnabled(False)
        self.showROICheckBox.stateChanged.connect(self.showhideROI)
        self.removeROIPushButton=QPushButton('Remove ROI')
        self.transROILabel=QLabel('Transformed ROI Dimensions')
        self.hROILayout=QHBoxLayout()
        self.transROIHLabel=QLabel('H:')
        self.transROIHLineEdit=QLineEdit('100')
        self.hROILayout.addWidget(self.transROIHLabel)
        self.hROILayout.addWidget(self.transROIHLineEdit)
        self.transROIHLineEdit.setValidator(self.intValidator)
        self.transROIHLineEdit.returnPressed.connect(self.get_ROI_pos)
        self.transROIHLineEdit.setEnabled(False)
        self.vROILayout = QHBoxLayout()
        self.transROIVLabel = QLabel('V:')
        self.transROIVLineEdit = QLineEdit('100')
        self.vROILayout.addWidget(self.transROIVLabel)
        self.vROILayout.addWidget(self.transROIVLineEdit)
        self.transROIVLineEdit.setValidator(self.intValidator)
        self.transROIVLineEdit.returnPressed.connect(self.get_ROI_pos)
        self.transROIVLineEdit.setEnabled(False)
        self.transImageLabel = QLabel('Transformed Image Dimensions')
        self.hImageLayout = QHBoxLayout()
        self.transImageHLabel = QLabel('H:')
        self.transImageHLineEdit = QLineEdit('1290')
        self.hImageLayout.addWidget(self.transImageHLabel)
        self.hImageLayout.addWidget(self.transImageHLineEdit)
        self.transImageHLineEdit.setValidator(self.intValidator)
        self.transImageHLineEdit.returnPressed.connect(self.imageDimChanged)
        self.transImageHLineEdit.setEnabled(False)
        self.vImageLayout = QHBoxLayout()
        self.transImageVLabel = QLabel('V:')
        self.transImageVLineEdit = QLineEdit('720')
        self.vImageLayout.addWidget(self.transImageVLabel)
        self.vImageLayout.addWidget(self.transImageVLineEdit)
        self.transImageVLineEdit.setValidator(self.intValidator)
        self.transImageVLineEdit.returnPressed.connect(self.imageDimChanged)
        self.transImageVLineEdit.setEnabled(False)
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
        control_vbox.addWidget(self.transROILabel)
        control_vbox.addLayout(self.hROILayout)
        control_vbox.addLayout(self.vROILayout)
        control_vbox.addWidget(self.transImageLabel)
        control_vbox.addLayout(self.hImageLayout)
        control_vbox.addLayout(self.vImageLayout)
        control_vbox.addWidget(self.transformCheckBox)
        spacer_item=QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        control_vbox.addItem(spacer_item)
        # set the vbox layout as the widgets layout
        hbox.addLayout(img_vbox)
        hbox.addLayout(control_vbox)
        self.setLayout(hbox)
        self.imageDimChanged()

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    def addROI(self):
        self.ROI=pg.PolyLineROI(self.pos,closed=True,pos=self.pos[0],pen=pg.mkPen('red',width=2))
        self.image_widget.imageView.view.addItem(self.ROI)
        self.addROIPushButton.setEnabled(False)
        self.removeROIPushButton.setEnabled(True)
        self.showROICheckBox.setEnabled(True)
        self.showROICheckBox.setChecked(True)
        self.transformCheckBox.setEnabled(True)
        self.get_ROI_pos()
        self.ROI.sigRegionChangeFinished.connect(self.get_ROI_pos)
        self.transROIHLineEdit.setEnabled(True)
        self.transROIVLineEdit.setEnabled(True)
        self.transImageHLineEdit.setEnabled(True)
        self.transImageVLineEdit.setEnabled(True)


    def get_ROI_pos(self):

        handles=self.ROI.getSceneHandlePositions()
        self.ROI_pos=[]
        for handle in handles[:2]:
            pointer = self.image_widget.imageView.getView().vb.mapSceneToView(handle[1])
            x, y = pointer.x(), pointer.y()
            self.ROI_pos.append([x, y])
        for handle in handles[3:1:-1]:
            pointer = self.image_widget.imageView.getView().vb.mapSceneToView(handle[1])
            x, y = pointer.x(), pointer.y()
            self.ROI_pos.append([x, y])
        self.ROI_pos=np.float32(self.ROI_pos)
        h=int(self.transROIHLineEdit.text())
        v=int(self.transROIVLineEdit.text())
        self.new_pos=np.float32([[0,0],[h,0],[0,v],[h,v]])+self.ROI_pos[0]
        self.resmat=cv2.getPerspectiveTransform(self.ROI_pos,self.new_pos)

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
        self.transROIVLineEdit.setEnabled(False)
        self.transROIHLineEdit.setEnabled(False)
        self.transImageVLineEdit.setEnabled(False)
        self.transImageHLineEdit.setEnabled(False)

    def showhideROI(self):
        if self.showROICheckBox.isChecked():
            self.ROI.show()
        else:
            self.ROI.hide()


    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    def imageDimChanged(self):
        self.imageH=int(self.transImageHLineEdit.text())
        self.imageV=int(self.transImageVLineEdit.text())

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        if self.transformCheckBox.isChecked():
            new_img = cv2.warpPerspective(cv_img, self.resmat, (self.imageH,self.imageV))
        else:
            new_img = cv_img
        self.image_widget.setImage(new_img.T,transpose=False)#,autoHistogramRange=False,autoLevels=False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = Camera_Widget()
    a.show()
    sys.exit(app.exec_())