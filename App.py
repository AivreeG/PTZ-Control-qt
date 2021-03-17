import cv2
import numpy as np
from PyQt5 import QtGui  
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QGridLayout, QSlider, QAction, qApp, QMainWindow, QDialog, QCheckBox, QRadioButton
from PyQt5.QtGui import QPixmap

from CameraController import CameraController
from VideoThread import VideoThread


class App(QMainWindow):
  def __init__(self, ipAddress):
    super().__init__()
    self.setWindowTitle("PTZ Controller")
    self.disply_width = 800
    self.display_height = 800

    self.content = QWidget(self)
    self.layout = QVBoxLayout()

    self.setCentralWidget(self.content)
    self.content.setLayout(self.layout)

    self.cam = CameraController(ipAddress)
    
    self.presetFunc = self.cam.recallPreset 


    # create the label that holds the image
    self.image_label = QLabel(self)
    self.image_label.setAlignment(Qt.AlignCenter)
    self.image_label.resize(self.disply_width, self.display_height)

    self.layout.addWidget(self.image_label)

    buttons = [ 
                [
                  {'widget': QPushButton('\\'), 'func': lambda : self.cam.movePositionRelative('8200', '7E00')}, 
                  {'widget': QPushButton('/\\'), 'func': lambda : self.cam.movePositionRelative('8000', '7E00')}, 
                  {'widget': QPushButton('/'), 'func': lambda : self.cam.movePositionRelative('7E00', '7E00')}
                ], 
                [
                  {'widget': QPushButton('<-'), 'func': lambda : self.cam.movePositionRelative('8200', '8000')}, 
                  {'widget': QPushButton('Home'), 'func': lambda : self.cam.movePositionAbsolute('8000', '8000')}, 
                  {'widget': QPushButton('->'), 'func': lambda : self.cam.movePositionRelative('7E00', '8000')}
                ], 
                [
                  {'widget': QPushButton('/'), 'func': lambda : self.cam.movePositionRelative('8200', '8200')},
                  {'widget': QPushButton('\\/'), 'func': lambda : self.cam.movePositionRelative('8000', '8200')},
                  {'widget': QPushButton('\\'), 'func': lambda : self.cam.movePositionRelative('7E00', '8200')}
                ] 
              ]
    presetButtons = [
                      [
                        {'widget': QPushButton('1'), 'func': lambda : self.cam.recallPreset('00')}, 
                        {'widget': QPushButton('2'), 'func': lambda : self.cam.recallPreset('01')}, 
                        {'widget': QPushButton('3'), 'func': lambda : self.cam.recallPreset('02')}
                      ], 
                      [
                        {'widget': QPushButton('4'), 'func': lambda : self.cam.recallPreset('03')}, 
                        {'widget': QPushButton('5'), 'func': lambda : self.cam.recallPreset('04')}, 
                        {'widget': QPushButton('6'), 'func': lambda : self.cam.recallPreset('05')}
                      ], 
                      [
                        {'widget': QPushButton('7'), 'func': lambda : self.cam.recallPreset('06')},
                        {'widget': QPushButton('8'), 'func': lambda : self.cam.recallPreset('07')},
                        {'widget': QPushButton('9'), 'func': lambda : self.cam.recallPreset('08')}
                      ] 
                    ]
    
    self.statusBar()

    exitAction = QAction('&Exit', self)        
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit application')
    exitAction.triggered.connect(qApp.quit)

    openCamera = QAction('&Open Camera', self)
    openCamera.setShortcut('Ctrl+O')
    openCamera.setStatusTip('Open Network Camera')
    openCamera.triggered.connect(self.openCameraModal)


    menubar = self.menuBar()
    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(exitAction)
    fileMenu.addAction(openCamera)

    buttonPanel = QGridLayout()

    slider = QSlider(Qt.Vertical)
    slider.setMinimum(0x555)
    slider.setMaximum(0xFFF)

    self.presetRadioButton = QRadioButton()

    if self.cam.isConnected():
      slider.setValue(int(self.cam.getZoom(), 16))
      slider.sliderReleased.connect(lambda : self.cam.setZoom(hex(slider.value())[2:].upper()))

    for row in presetButtons:
      for column in row:
        btn = column['widget']
        btn.pressed.connect(column['func'])
        # buttons.append(btn)
        buttonPanel.addWidget(btn, presetButtons.index(row), row.index(column))

    for row in buttons:
      for column in row:
        btn = column['widget']
        btn.pressed.connect(column['func'])
        # buttons.append(btn)
        buttonPanel.addWidget(btn, buttons.index(row), row.index(column) + 4)

    buttonPanel.addWidget(slider, 0, 7, 3, 7)

    self.layout.addLayout(buttonPanel)
    

    # cv2.setMouseCallback('PTZ Controller', self.draw_circle) 

    # create the video capture thread
    self.thread = VideoThread(self.cam)
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

  def setPresetFunc(self, type):
    funcs = {'recall': self.cam.recallPreset, 'save': self.cam.savePreset, 'delete': self.cam.deletePreset}
    self.presetFunc = funcs[type]

  def draw_circle(self, event,x,y,flags,param):  
    if event == cv2.EVENT_LBUTTONDBLCLK:  
      cv2.circle(img,(x,y),50,(123,125, 200),-1)