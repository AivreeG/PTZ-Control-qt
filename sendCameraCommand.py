#!/usr/bin/python

import sys
from CameraController import CameraController

# IPs = ['10', '11', '12', '13']
IPs = ['12', '13']


if __name__ == '__main__':
  if len(sys.argv) < 3:
    print('Usage: sendCommand.py <camID> [group] <cmd> [values]')
    exit(1)

  ip = IPs[int(sys.argv[1])]
  # camIP = '192.168.1.' + ip
  camIP = '192.168.0.' + ip
  
  options = False

  group = sys.argv[2]
  cmd = sys.argv[3]
  if sys.argv[-1][0:2] == '--':
    values = sys.argv[4:-1]
    options = True
  else:
    values = sys.argv[4:]

  CameraController.quickCommand(camIP, CameraController.COMMANDS[group][cmd], *values)
