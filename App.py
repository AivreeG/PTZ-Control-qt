import cv2
import numpy as np
from PyQt5 import QtGui  
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QGridLayout, QSlider, QAction, qApp, QMainWindow, QDialog
from PyQt5.QtGui import QPixmap

from CameraController import CameraController
from VideoThread import VideoThread


class App(QMainWindow):
  def __init__(self, ipAddress):
    super().__init__()
    self.setWindowTitle("PTZ Controller")
    self.disply_width = 800
    self.display_height = 800
    # create the label that holds the image
    self.image_label = QLabel(self)
    self.image_label.setAlignment(Qt.AlignCenter)
    self.image_label.resize(self.disply_width, self.display_height)

    self.setCentralWidget(self.image_label)

    # ipAddress = '192.168.1.13'

    cam = ipAddress and CameraController(ipAddress) or None

    buttons = [ 
                [
                  {'widget': QPushButton('\\'), 'func': lambda : cam.movePositionRelative('8200', '7E00')}, 
                  {'widget': QPushButton('/\\'), 'func': lambda : cam.movePositionRelative('8000', '7E00')}, 
                  {'widget': QPushButton('/'), 'func': lambda : cam.movePositionRelative('7E00', '7E00')}
                ], 
                [
                  {'widget': QPushButton('<-'), 'func': lambda : cam.movePositionRelative('8200', '8000')}, 
                  {'widget': QPushButton('Home'), 'func': lambda : cam.movePositionAbsolute('8000', '8000')}, 
                  {'widget': QPushButton('->'), 'func': lambda : cam.movePositionRelative('7E00', '8000')}
                ], 
                [
                  {'widget': QPushButton('/'), 'func': lambda : cam.movePositionRelative('8200', '8200')},
                  {'widget': QPushButton('\\/'), 'func': lambda : cam.movePositionRelative('8000', '8200')},
                  {'widget': QPushButton('\\'), 'func': lambda : cam.movePositionRelative('7E00', '8200')}
                ] 
              ]
    # create a vertical box layout and add the two labels
    # layout = QGridLayout()
    # layout.addWidget(self.image_label, 0, 0, 8, 10)
    # slider = QSlider(Qt.Vertical)
    # slider.setMinimum(0x555)
    # slider.setMaximum(0xFFF)
    # if cam != None:
    #   slider.setValue(int(cam.zoom, 16))
    #   slider.sliderReleased.connect(lambda : cam.setZoom(hex(slider.value())[2:].upper()))

    # for row in buttons:
    #   for column in row:
    #     btn = column['widget']
    #     btn.pressed.connect(column['func'])
    #     # buttons.append(btn)
    #     layout.addWidget(btn, buttons.index(row) + 11, row.index(column) + 4)

    # layout.addWidget(slider, 9, 7, 12, 7)          
        
    exitAction = QAction('&Exit', self)        
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit application')
    exitAction.triggered.connect(qApp.quit)

    openCamera = QAction('&Open Camera', self)
    openCamera.setShortcut('Ctrl+O')
    openCamera.setStatusTip('Open Network Camera')
    openCamera.triggered.connect(self.openCameraModal)

    self.statusBar()

    menubar = self.menuBar()
    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(exitAction)
    fileMenu.addAction(openCamera)

    # set the vbox layout as the widgets layout
    # self.setLayout(layout)
    
    # cv2.setMouseCallback('PTZ Controller', self.draw_circle) 

    # create the video capture thread
    self.thread = VideoThread(cam)
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
    qt_img = self.convert_cv_qt(cv_img)
    self.image_label.setPixmap(qt_img)
  
  def convert_cv_qt(self, cv_img):
    """Convert from an opencv image to QPixmap"""
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
    p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
    return QPixmap.fromImage(p)

  def openCameraModal(self):
    self.cameraModal = QDialog(self)
    self.cameraModal.exec()

  def draw_circle(self, event,x,y,flags,param):  
    if event == cv2.EVENT_LBUTTONDBLCLK:  
      cv2.circle(img,(x,y),50,(123,125, 200),-1)