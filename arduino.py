#!/usr/bin/env python
# coding: utf-8

# In[4]:


# ボードに書き込んで一回リセットボタン押して安定した後実行する
# python側が起動するまでarduinoは待ってくれる
import serial
from time import sleep


# In[5]:


COM = '/dev/cu.usbmodem14301'
RATE = 9600
ser = serial.Serial(COM, RATE, timeout=0.1)


# In[ ]:


class ArduinoController(object):
    
    def __init__(self, com, baudrate=9600):
        # クラス特有のパラメータ
        self.COM = port
        self.BAUDRATE = baudrate
        self.SERIAL = serial.Serial(COM, RATE, timeout=0.1)
        
        # Controller共通パラメータ
        self.scale = {}
        self.assigned_params = []
        self.threshold = 0.001
        self.pre_mult = {}
        self.offset_sofar = {}
        
    def standby(self, synth):
        self.parent = synth
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
    
    def assign(self, parameter, scale=None):
        self.scale[parameter] = scale
        self.pre_mult[parameter] = [0] * 128
        self.offset_sofar[parameter] = [0] * 128
        if parameter.__class__.__name__ == "Parameter":
            if parameter.controllable == True:
                self.assigned_params.append(parameter)
            else:
                raise InvalidParameterAssignment("This parameter cannot to be assigned.")
        else:
            raise InvalidParameterAssignment("This parameter cannot to be assigned.")
            
    def update(self, module):
        for param in self.assigned_params:
            if param.parent == module:
                self._adsr(param)
                
    def _adsr(self, parameter):
        for i in range(128):
            data = self.SERIAL.read_all()
            data = data.decode()
            data = parameter.inival[i] + scale[parameter]*int(data) / 255
            parameter.fix(data, i)
            


# In[ ]:


# while True:
#     data = ser.read_all()
#     print(data.decode())
#     sleep(0.5)
# ser.close()


# In[ ]:




