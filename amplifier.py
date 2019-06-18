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
        
        self.flag = False
        
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
        if self.stream.is_active():
            #if self.flag == True:
             #   self.thread1.join()
              #  self.flag == False
                
            #self.thread1 = threading.Thread(target=self.stream.write, args=(output,)) 
            #self.thread1.start()
            #self.flag = True
            self.stream.write(output)


# In[ ]:




