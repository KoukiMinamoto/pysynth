#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pyaudio
import threading
import wave
from synth import *


# In[2]:


class SimpleAmp():
    def __init__(self, volume=1.0):
        self.name = "SimpleAmp"
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 512
        self.volume = volume
        
        self.amp = Parameter(np.zeros(self._BUF_SIZE), self, -32768, 32767, name="amp", controllable=True)
        
    def standby(self, synth):
        self.parent = synth
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
        
    def play(self):
        for i in range(128):
            #print(np.shape(self.parent.wave_data.get(i)))
            self.amp.fix(self.volume*self.parent.wave_data.get(i), i)        


# In[ ]:


class WavWriter():
    def __init__(self, volume=1.0, file_name=""):
        self.name = "WavWriter"
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
        self.volume = volume
        self.file_name = file_name
        
        self.amp = Parameter(np.zeros(self._BUF_SIZE), self, -32768, 32767, name="amp", controllable=True)
        
    def standby(self, synth):
        self.parent = synth
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
        
        self.parent.out_file_name = self.file_name
        self.parent.file_out = True
        
        
    def play(self):
        for i in range(128):
            self.amp.fix(self.volume*self.parent.wave_data.get(i), i)

