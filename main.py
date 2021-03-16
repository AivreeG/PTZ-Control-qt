#!/usr/bin/python

import sys
from PyQt5.QtWidgets import QApplication

from App import App

__version__ = '0.1'
__author__ = 'Aivree Gomez'
		
if __name__=="__main__":
  app = QApplication(sys.argv)
  if len(sys.argv) == 2:
    a = App(sys.argv[1])
    a.show()
  elif len(sys.argv) == 1:
    a = App(None)
    a.show()
  else:
    print("Usage: main.py [IP Address/Hostname]")
  sys.exit(app.exec())