import socket
import sys
import urllib.parse
import urllib.request
from PyQt5.QtCore import pyqtSignal, Qt, QThread

class CameraController(Qthread):
  COMMANDS = {
      'preset': {
        'save': 'M',
        'recall': 'R',
        'delete': 'C',
        'getLast': 'S',
      },
      'panTilt': {
        'moveAbsolute': 'APC',
        'moveRelative': 'RPC',
        'moveSpeedAbsolute': 'APS',
        'moveSpeedRelative': 'RPS'
      },
      'move': {
        'pan': 'P',
        'tilt': 'T',
        'panTilt': 'PTS'
      },
      'zoom': {
        'set': 'AXZ',
        'get': 'GZ',
        'setSpeed': 'Z'
      }
  }
  home = '80008000' 

  def __init__(self, ipAddress=None):
    super().__init__()
    self.connected = ipAddress and True or False
    self.zoom_signal = pyqtSignal(str)
    self._run_flag = False

    if self.connected:
      self.connect(ipAddress)
      self.connection, self.client_ip = self.connectNotify(ipAddress)
      if self.socket != None:
        print(sys.stderr, 'client connected:', self.client_ip)
        self._run_flag = True
    
  def connect(self, ipAddress):
    self.ipAddress = ipAddress
    self.position = self.getPosition()
    self.zoom = self.getZoom()
    self.speed = self.getSpeed()

  def isConnected(self):
    return self.connected

  def connectNotify(self, ipAddress):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', 31004)
    print(sys.stderr, 'starting up on %s port %s' % server_address)
    sock.bind(server_address)
    sock.listen(1)

    # Probably don't need this
    # numSessions = 0
    # sessions_url = f'http://{self.ipAddress}//cgi-bin/man_session' + '?' + urllib.parse.urlencode({'command': 'get'})
    # with urllib.request.urlopen(sessions_url) as response:
    #   numSessions = response.read().decode('utf-8')[14:]
    #   print('Current Sessions: ' + numSessions)

    getVars = {'connect': 'start', 'my_port': server_address[1], 'uid': 0}
    url = f'http://{self.ipAddress}/cgi-bin/event'
    full_url = url + '?' + urllib.parse.urlencode(getVars)
    with urllib.request.urlopen(full_url) as response:
      val = response.read().decode('utf-8')
      print('Connect Notify: ' + val)

    print(sys.stderr, 'waiting for a connection')
    return sock.accept()

  def run(self):
    try:
      while self._run_flag:
        data = connection.recv(576)
        self.zoom_signal.emit(data)
    finally:
        # Clean up the connection
        self.connection.close()
    
  def sendCommand(self, command, data):
    if not self.connected:
      print(f"#{command}{data}")
      return 'NC'
    getVars = {'cmd': f"#{command}{data}", 'res': 1}
    url = f'http://{self.ipAddress}/cgi-bin/aw_ptz'
    full_url = url + '?' + urllib.parse.urlencode(getVars)
    with urllib.request.urlopen(full_url) as response:
      val = response.read().decode('utf-8')
      print(getVars['cmd'] + ' : ' + val)
      return val

  def movePositionAbsolute(self, pan, tilt, speed=-1, table=-1):
    command = ''
    args = pan + tilt

    if speed != -1 and table != -1:
      command = CameraController.COMMANDS['panTilt']['moveSpeedAbsolute']
      args += speed + table
    else:
      command = CameraController.COMMANDS['panTilt']['moveAbsolute']

    return self.sendCommand(command, args)

  def movePositionRelative(self, pan, tilt, speed=-1, table=-1):
    command = ''
    args = pan + tilt

    if speed != -1 and table != -1:
      command = CameraController.COMMANDS['panTilt']['moveSpeedRelative']
      args += speed + table
    else:
      command = CameraController.COMMANDS['panTilt']['moveRelative']
  
    return self.sendCommand(command, args)

  def moveTilt(self, speed):
    return self.sendCommand(CameraController.COMMANDS['move']['tilt'], speed)

  def movePan(self, speed):
    return self.sendCommand(CameraController.COMMANDS['move']['pan'], speed)

  def movePanTilt(self, panSpeed, tiltSpeed):
    return self.sendCommand(CameraController.COMMANDS['move']['panTilt'], panSpeed + tiltSpeed)

  def stopTilt(self):
    return self.moveTilt('50')

  def stopPan(self):
    return self.movePan('50')

  def stopPanTilt(self):
    return self.movePanTilt('50', '50')

  def getSpeed(self):
    return self.sendCommand(CameraController.COMMANDS['move']['panTilt'], '')[2:]

  def getSpeed(self):
    return self.sendCommand(CameraController.COMMANDS['move']['panTilt'], '')[2:]

  def movementSpeed(self, speed):
    return self.sendCommand(CameraController.COMMANDS['panTilt']['speed'], speed)

  def setZoom(self, level):
    return self.sendCommand(CameraController.COMMANDS['zoom']['set'], level)

  def getZoom(self):
    return self.sendCommand(CameraController.COMMANDS['zoom']['get'], '')[2:]

  def setZoomSpeed(self, speed):
    return self.sendCommand(CameraController.COMMANDS['zoom']['setSpeed'], speed)

  def savePreset(self, preset):
    return self.sendCommand(CameraController.COMMANDS['preset']['save'], f"{(preset - 1):02d}")

  def recallPreset(self, preset):
    response = self.sendCommand(CameraController.COMMANDS['preset']['recall'], f"{(preset - 1):02d}")
    self.zoom = self.getZoom()
    return response

  def deletePreset(self, preset):
    self.sendCommand(CameraController.COMMANDS['preset']['delete'], f"{(preset - 1):02d}")

  def getLastPreset(self):
    return self.sendCommand(CameraController.COMMANDS['preset']['getLast'], '')

  def getPosition(self):
    return self.sendCommand(CameraController.COMMANDS['panTilt']['moveAbsolute'], '')

  def goHome(self):
    return self.sendCommand(CameraController.COMMANDS['panTilt']['moveAbsolute'], CameraController.home)
  
  def getVideo(self):
    return f'http://{self.ipAddress}/cgi-bin/mjpeg?resolution=640x360&framerate=30&quality=1'