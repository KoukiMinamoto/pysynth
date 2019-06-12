#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pyaudio
import threading


# In[3]:


class SimpleAmp():
    
    def __init__(self):
        self.name = "SimpleAmp"
        self.val = None
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
    
    def _standby(self, stream, pitch=440, rate=44100, bufsize=500):
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        self.stream = stream
        
        return [self.name]
    
    def _play(self, wave):
        self._output(wave)
    
    def _output(self, wave):
        if len(wave) > 0:
            output = wave
        else:
            pass
        
        self.stream.write(output.astype(np.float32).tostring())


# In[ ]:




