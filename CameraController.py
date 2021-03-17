import sys
import urllib.parse
import urllib.request

class CameraController:
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
        'speed': 'P',
        'moveSpeedAbsolute': 'APS',
        'moveSpeedRelative': 'RPS'
      },
      'zoom': {
        'set': 'AXZ',
        'get': 'GZ',
        'setSpeed': 'Z'
      }
  }
  home = '80008000' 

  def __init__(self, ipAddress=None):
    self.connected = ipAddress and True or False

    if self.connected:
      self.connect(ipAddress)
    
  def connect(self, ipAddress):
    self.ipAddress = ipAddress
    self.position = self.getPosition()
    self.zoom = self.getZoom()
  def isConnected(self):
    return self.connected
    
  def sendCommand(self, command, data):
    if not self.connected:
      return 'NC'
    getVars = {'cmd': f'#{command}{data}', 'res': 1}
    url = f'http://{self.ipAddress}/cgi-bin/aw_ptz'
    full_url = url + '?' + urllib.parse.urlencode(getVars)
    with urllib.request.urlopen(full_url) as response:
      val = response.read().decode('utf-8')
      print(val)
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

  def movementSpeed(self, speed):
    return self.sendCommand(CameraController.COMMANDS['panTilt']['speed'], speed)

  def setZoom(self, level):
    return self.sendCommand(CameraController.COMMANDS['zoom']['set'], level)

  def getZoom(self):
    return self.sendCommand(CameraController.COMMANDS['zoom']['get'], '')[2:]

  def setZoomSpeed(self, speed):
    return self.sendCommand(CameraController.COMMANDS['zoom']['setSpeed'], speed)

  def savePreset(self, preset):
    return self.sendCommand(CameraController.COMMANDS['preset']['save'], preset)

  def recallPreset(self, preset):
    return self.sendCommand(CameraController.COMMANDS['preset']['recall'], preset)

  def deletePreset(self, preset):
    self.sendCommand(CameraController.COMMANDS['preset']['delete'], preset)

  def getLastPreset(self):
    return self.sendCommand(CameraController.COMMANDS['preset']['getLast'], '')

  def getPosition(self):
    return self.sendCommand(CameraController.COMMANDS['panTilt']['moveAbsolute'], '')

  def goHome(self):
    return self.sendCommand(CameraController.COMMANDS['panTilt']['moveAbsolute'], CameraController.home)
  
  def getVideo(self):
    return f'http://{self.ipAddress}/cgi-bin/mjpeg?resolution=640x360&framerate=30&quality=1'