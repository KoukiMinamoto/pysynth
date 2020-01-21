#!/usr/bin/env python
# coding: utf-8

# In[12]:


import numpy as np
import scipy
import serial
from synth import *
import error


# In[ ]:


class Controller(object):
    pass


# In[3]:


class Envelope(Controller):

    def __init__(self, A=0.1, D=0.1, S=1.0, R=0.1):
        self.A = A
        self.D = D
        self.S = S
        self.R = R
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
        
        self._Aframe = self.A * self._RATE
        self._Dframe = self.D * self._RATE
        self._Rframe = self.R * self._RATE
    
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
        if parameter.name == "amp":
            for i in range(128):
                offset = self.parent.offset.get(i)
                if  offset <= self._Aframe and offset >= 0 and self.parent.R_flag.get(i) == False:
                    factor = 1.0 / (self._Aframe+1)
                    bias = 0
                    mult = bias + offset*factor
                    parameter.fix(parameter.get(i)*mult, i)
                    self.pre_mult[parameter][i] = mult
                    self.offset_sofar[parameter][i] = offset
                elif offset > self._Aframe and offset <= (self._Aframe+self._Dframe) and self.parent.R_flag.get(i) == False:
                    factor = (self.S - 1.0) / (self._Dframe+1)
                    bias = 1.0
                    mult = bias + ((offset)-self._Aframe)*factor
                    parameter.fix(parameter.get(i)*mult, i)
                    self.pre_mult[parameter][i] = mult
                    self.offset_sofar[parameter][i] = offset
                elif offset > (self._Aframe + self._Dframe) and self.parent.R_flag.get(i) != True:
                    factor = self.S
                    bias = 0
                    mult = bias + factor
                    parameter.fix(parameter.get(i)*factor, i)
                    self.pre_mult[parameter][i] = mult
                    self.offset_sofar[parameter][i] = offset
                elif self.parent.R_flag.get(i) == True:
                    factor = (self.pre_mult[parameter][i]) / (self._Rframe+1)
                    bias = self.pre_mult[parameter][i]
                    mult = bias - factor*(offset-self.offset_sofar[parameter][i])
                    parameter.fix(parameter.get(i)*mult, i)
                    if mult <= self.threshold:
                        self.parent.offset.fix(0, i)
                        self.parent.velocity.fix(0, i)
                        self.parent.R_flag.fix(False, i)
                else:
                    pass
                    
                    
            
        else:
            for i in range(128):
                offset = self.parent.offset.get(i)
                # Attack区間にデータがあるとき
                if  offset <= self._Aframe and offset >= 0 and self.parent.R_flag.get(i) == False:
                    factor = self.scale[parameter] / (self._Aframe+1)
                    bias = parameter.inival[i]
                    mult = offset*factor
                    parameter.fix(bias + mult, i)
                    self.pre_mult[parameter][i] = mult
                    self.offset_sofar[parameter][i] = offset
                # Decay区間にデータがある時
                elif offset > self._Aframe and offset <= (self._Aframe+self._Dframe) and self.parent.R_flag.get(i) == False:
                    factor = (1.0 - self.S)*self.scale[parameter] / (self._Dframe+1)
                    bias = self.scale[parameter]
                    mult = bias - (offset-self._Aframe)*factor
                    parameter.fix(parameter.inival[i]+mult, i)
                    self.pre_mult[parameter][i] = mult
                    self.offset_sofar[parameter][i] = offset
                # Sustain区間にあるとき
                elif offset > (self._Aframe + self._Dframe) and self.parent.R_flag.get(i) != True:
                    factor = self.S * self.scale[parameter]
                    bias = parameter.inival[i]
                    mult = factor
                    parameter.fix(bias + factor, i)
                    self.pre_mult[parameter][i] = mult
                    self.offset_sofar[parameter][i] = offset
                # Release区間にあるとき
                elif self.parent.R_flag.get(i) == True:
                    factor = (self.pre_mult[parameter][i]) / (self._Rframe+1)
                    bias = parameter.inival[i] + self.pre_mult[parameter][i]
                    mult = factor*(offset-self.offset_sofar[parameter][i])
                    #print("mult: ", mult)
                    parameter.fix(bias - mult, i)
                else:
                    pass


# In[ ]:


class ArduinoController(object):
    # ボードに書き込んで一回リセットボタン押して安定した後実行する
    # python側が起動するまでarduinoは待ってくれる
    def __init__(self, com, baudrate=9600):
        # クラス特有のパラメータ
        self.COM = com
        self.BAUDRATE = baudrate
        self.SERIAL = serial.Serial(self.COM, self.BAUDRATE, timeout=0.1)
        self.data = []
        self.delta = 0.0
        
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
            data_cur = self.SERIAL.read_all()
            data_cur = data_cur.decode()
            #print("送られてきたデータ")
            #print(data_cur)
            if data_cur != '':
                self.data = data_cur.split("\r\n")
                #print("値が変わりました。")
            try:
                self.delta = float(self.data[0])
                #print(self.delta)
            except ValueError:
                pass
            #print(data)
            # gForceXをパラメータにとった場合
            #data = parameter.inival[i] + self.scale[parameter]*self.delta
            # rotXをパラメータにとった場合
            #data = parameter.get(i) + 0.1*self.delta
            # rollをパラメータにとった場合
            data = parameter.inival[i] + self.scale[parameter] * self.delta / 180.0
            parameter.fix(data, i)

