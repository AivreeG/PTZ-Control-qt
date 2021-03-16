#!/usr/bin/python

import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QGridLayout, QSlider

from CameraController import CameraController


app = QApplication(sys.argv)

ipAddress = '192.168.1.13'

cam = CameraController(ipAddress)

buttons = [ 
						[
							{'label': '\\', 'func': lambda : cam.movePositionRelative('8200', '7E00')}, 
							{'label': '/\\', 'func': lambda : cam.movePositionRelative('8000', '7E00')}, 
							{'label': '/', 'func': lambda : cam.movePositionRelative('7E00', '7E00')}
						], 
						[
							{'label': '<-', 'func': lambda : cam.movePositionRelative('8200', '8000')}, 
							{'label': 'Home', 'func': lambda : cam.movePositionAbsolute('8000', '8000')}, 
							{'label': '->', 'func': lambda : cam.movePositionRelative('7E00', '8000')}
						], 
						[
							{'label': '/', 'func': lambda : cam.movePositionRelative('8200', '8200')},
							{'label': '\\/', 'func': lambda : cam.movePositionRelative('8000', '8200')},
							{'label': '\\', 'func': lambda : cam.movePositionRelative('7E00', '8200')}
						] 
					]


window = QWidget()
window.setWindowTitle('PTZ Controller')
window.setGeometry(100, 100, 400, 100)
window.move(900, 500)
layout = QGridLayout()
slider = QSlider(Qt.Vertical)
slider.setMinimum(0x555)
slider.setMaximum(0xFFF)
slider.setValue(int(cam.zoom, 16))
slider.sliderReleased.connect(lambda : cam.setZoom(hex(slider.value())[2:].upper()))

for row in buttons:
	for column in row:
		btn = QPushButton(column['label'])
		btn.pressed.connect(column['func'])
		# buttons.append(btn)
		layout.addWidget(btn, buttons.index(row), row.index(column))

layout.addWidget(slider, 0, 3, 3, 3)

window.setLayout(layout)

window.show()

sys.exit(app.exec_())

