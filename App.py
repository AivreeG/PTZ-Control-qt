import cv2
import numpy as np
from PyQt5 import QtGui  
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import (
  QWidget, 
  QLabel, 
  QVBoxLayout, 
  QPushButton, 
  QGridLayout, 
  QSlider, 
  QAction, 
  qApp, 
  QMainWindow, 
  QDialog, 
  QCheckBox, 
  QRadioButton, 
  QSpacerItem,
  QSizePolicy
)
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
                  {'widget': QPushButton('\\'), 'pressFunc': lambda : self.cam.movePanTilt('20', '80'), 'releaseFunc': lambda : self.cam.stopPanTilt()}, 
                  {'widget': QPushButton('/\\'), 'pressFunc': lambda : self.cam.moveTilt('80'), 'releaseFunc': lambda : self.cam.stopTilt()}, 
                  {'widget': QPushButton('/'), 'pressFunc': lambda : self.cam.movePanTilt('80', '80'), 'releaseFunc': lambda : self.cam.stopPanTilt()}
                ], 
                [
                  {'widget': QPushButton('<-'), 'pressFunc': lambda : self.cam.movePan('20'), 'releaseFunc': lambda : self.cam.stopPan()}, 
                  {'widget': QPushButton('Home'), 'pressFunc': lambda : self.cam.movePositionAbsolute('8000', '8000'), 'releaseFunc': lambda : None}, 
                  {'widget': QPushButton('->'), 'pressFunc': lambda : self.cam.movePan('80'), 'releaseFunc': lambda : self.cam.stopPan()}
                ], 
                [
                  {'widget': QPushButton('/'), 'pressFunc': lambda : self.cam.movePanTilt('20', '20'), 'releaseFunc': lambda : self.cam.stopPanTilt()},
                  {'widget': QPushButton('\\/'), 'pressFunc': lambda : self.cam.moveTilt('20'), 'releaseFunc': lambda : self.cam.stopTilt()},
                  {'widget': QPushButton('\\'), 'pressFunc': lambda : self.cam.movePanTilt('80', '20'), 'releaseFunc': lambda : self.cam.stopPanTilt()}
                ] 
              ]
    presetButtons = [
                      [
                        {'widget': QPushButton('1'), 'func': lambda : self.presetFunc(1)}, 
                        {'widget': QPushButton('2'), 'func': lambda : self.presetFunc(2)}, 
                        {'widget': QPushButton('3'), 'func': lambda : self.presetFunc(3)}
                      ], 
                      [
                        {'widget': QPushButton('4'), 'func': lambda : self.presetFunc(4)}, 
                        {'widget': QPushButton('5'), 'func': lambda : self.presetFunc(5)}, 
                        {'widget': QPushButton('6'), 'func': lambda : self.presetFunc(6)}
                      ], 
                      [
                        {'widget': QPushButton('7'), 'func': lambda : self.presetFunc(7)},
                        {'widget': QPushButton('8'), 'func': lambda : self.presetFunc(8)},
                        {'widget': QPushButton('9'), 'func': lambda : self.presetFunc(9)}
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

    self.zoomSlider = QSlider(Qt.Vertical)
    self.zoomSlider.setMinimum(0x555)
    self.zoomSlider.setMaximum(0xFFF)

    buttonPanel.addWidget(self.zoomSlider, 0, 8, 3, 7) #, Qt.AlignHCenter)

    speedSlider = QSlider(Qt.Vertical)
    speedSlider.setMinimum(0)
    speedSlider.setMaximum(49)

    buttonPanel.addWidget(speedSlider, 0, 4, 3, 7) #, alignment=Qt.AlignHCenter)

    zoomLabel = QLabel('Zoom')
    buttonPanel.addWidget(zoomLabel, 4, 8)

    speedLabel = QLabel('Speed')
    buttonPanel.addWidget(speedLabel, 4, 4)

    if self.cam.isConnected():
      zoomSlider.setValue(int(self.cam.getZoom(), 16))
      zoomSlider.sliderReleased.connect(lambda : self.cam.setZoom(hex(zoomSlider.value())[2:].upper()))
      speedSlider.setValue(self.cam.getSpeed())
      speedSlider.sliderReleased.connect(lambda : self.cam.setSpeed(speedSlider.value())[2:])

    for row in presetButtons:
      for column in row:
        btn = column['widget']
        btn.pressed.connect(column['func'])
        # buttons.append(btn)
        buttonPanel.addWidget(btn, presetButtons.index(row), row.index(column) )

    recallPresetRadio = QRadioButton("Recall")
    recallPresetRadio.setChecked(True)
    recallPresetRadio.toggled.connect(lambda : self.setPresetFunc(recallPresetRadio.text()))
    buttonPanel.addWidget(recallPresetRadio, 4, 0)

    savePresetRadio = QRadioButton("Save") 
    savePresetRadio.setChecked(False)
    savePresetRadio.toggled.connect(lambda : self.setPresetFunc(savePresetRadio.text()))
    buttonPanel.addWidget(savePresetRadio, 4, 1)

    deletePresetRadio = QRadioButton("Delete") 
    deletePresetRadio.setChecked(False)
    deletePresetRadio.toggled.connect(lambda : self.setPresetFunc(deletePresetRadio.text()))
    buttonPanel.addWidget(deletePresetRadio, 4, 2)
    
    # num = 1
    # for x in range(3):
    #   for y in range(3):
    #     btn = QPushButton(str(num))
    #     btn.pressed.connect(lambda : self.presetFunc(num)) #Returns last value only
    #     buttonPanel.addWidget(btn, x, y)
    #     num += 1

    for row in buttons:
      for column in row:
        btn = column['widget']
        btn.pressed.connect(column['pressFunc'])
        btn.released.connect(column['releaseFunc'])
        # buttons.append(btn)
        buttonPanel.addWidget(btn, buttons.index(row), row.index(column) + 5)


    # spacerItem = QSpacerItem(150, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

    # buttonPanel.addItem(spacerItem, 0,8)

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

  @pyqtSlot(str)
  def update_zoom(self, value):
    # self.zoomSlider.setValue(int(value, 16))
    print('Zoom Update: ' + value)

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
    self.presetFunc = funcs[type.lower()]

  def draw_circle(self, event,x,y,flags,param):  
    if event == cv2.EVENT_LBUTTONDBLCLK:  
      cv2.circle(img,(x,y),50,(123,125, 200),-1)