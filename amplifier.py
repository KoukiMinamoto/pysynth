#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np
import pyaudio
import threading
from synth import *


# In[5]:


class SimpleAmp():
    def __init__(self, volume=1.0):
        self.name = "SimpleAmp"
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
        self.volume = volume
        
        self.amp = Parameter(np.zeros(self._BUF_SIZE), self, -32768, 32767, name="amp", controllable=True)
        
    def standby(self, synth, pitch=440, rate=44100, bufsize=500):
        self.parent = synth
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        
    def play(self):
        for i in range(128):
            self.amp.fix(self.volume*self.parent.wave_data.get(i), i)        


# In[3]:


class _SimpleAmp():
    
    def __init__(self):
        self.name = "SimpleAmp"
        self.val = None
        
        self.flag = False
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
    
    def _standby(self, synth, pitch=440, rate=44100, bufsize=500):
        self.parent = synth
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        self.stream = self.partent.stream
        
        return self
    
    def _play(self, wave):
        self._output(wave)
    
    def _output(self, wave):
        if len(wave) > 0:
            output = wave
        else:
            pass
        if self.stream.is_active():
            #if self.flag == True:
             #   self.thread1.join()
              #  self.flag == False
                
            #self.thread1 = threading.Thread(target=self.stream.write, args=(output,)) 
            #self.thread1.start()
            #self.flag = True
            self.stream.write(output)

