import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

class VideoThread(QThread):
  change_pixmap_signal = pyqtSignal(np.ndarray)

  def __init__(self, camera):
    super().__init__()
    self._run_flag = True
    self.camera = camera

  def run(self):
    # capture from web cam
    if self.camera == None:
      no_cam_img = np.zeros((600,600,3), np.uint8) 
      cv2.putText(no_cam_img, 'No Camera Available', (150,300), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255))
      self.change_pixmap_signal.emit(no_cam_img)
    else:
      cap = cv2.VideoCapture(self.camera.getVideo())
      while self._run_flag:
        ret, cv_img = cap.read()
        if ret:
          self.change_pixmap_signal.emit(cv_img)
      cap.release()

  def stop(self):
    """Sets run flag to False and waits for thread to finish"""
    self._run_flag = False
    self.wait()