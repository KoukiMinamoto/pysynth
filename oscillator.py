#!/usr/bin/env python
# coding: utf-8

# In[3]:


import numpy as np
import scipy.signal
import wave
from synth import *


# In[15]:


class SineWave():
    """ * サイン波を生成するモジュール *
        -args: 
            Note_ON/OFF: list(128, 1)
            Velocity:    list(128, 1)
            
        -return: wave_data: list(128, BUFSIZE)
    """
    def __init__(self, interval=0, fine=0):
        self.name = "SineWave"
        
        self.interval = Parameter(interval, self, 0, 12, name="interval", controllable=True)
        self.fine = Parameter(fine, self, 0, 100,  name="fine", controllable=True)
        self.wave_data = Parameter(None, self, -32768, 32767, "wave_data")
        self.freq = Parameter(0, self, 0.0, None, "freq")
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
        
        for i in range(128):
            freq = self._PITCH * np.power(2, (self.interval.get(i)+i-69)/12)
            freq = freq * np.power(2, self.fine.get(i)/100)
            self.freq.fix(freq, i)
        
        
    def standby(self, synth, pitch=440, rate=44100, bufsize=500):
        self.parent = synth
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
    
    def play(self):
        self._sine()
        
    
    def _sine(self):
        wave_data = []
        offset = self.parent.offset
        vel = self.parent.velocity
        freq = self.freq
        
        for i in range(128):
            if offset.get(i) != -1:
                factor = float(freq.get(i)) * (np.pi*2) / self._RATE
                wave = np.sin(np.arange(offset.get(i), offset.get(i)+self._BUF_SIZE) * factor) * 32767/127 * vel.get(i)
                self.parent.wave_data.fix(wave, i)
            elif offset.get(i) == -1:
                pass


# In[ ]:


class SquareWave():
    
    def __init__(self, interval=0, fine=0):
        self.name = "SineWave"
        
        self.interval = Parameter(interval, self, 0, 12, name="interval", controllable=True)
        self.fine = Parameter(fine, self, 0, 100,  name="fine", controllable=True)
        self.wave_data = Parameter(None, self, -32768, 32767, "wave_data")
        self.freq = Parameter(0, self, 0.0, None, "freq")
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
        
        for i in range(128):
            freq = self._PITCH * np.power(2, (self.interval.get(i)+i-69)/12)
            freq = freq * np.power(2, self.fine.get(i)/100)
            self.freq.fix(freq, i)
        
        
    def standby(self, synth, pitch=440, rate=44100, bufsize=500):
        self.parent = synth
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
    
    def play(self):
        self._sine()
        
    
    def _sine(self):
        wave_data = []
        offset = self.parent.offset
        vel = self.parent.velocity
        freq = self.freq
        
        for i in range(128):
            if offset.get(i) != -1:
                factor = float(freq.get(i)) * (np.pi*2) / self._RATE
                wave = scipy.signal.square(np.arange(offset.get(i), offset.get(i)+self._BUF_SIZE) * factor) * 32767/127 * vel.get(i)
                self.parent.wave_data.fix(wave, i)
            elif offset.get(i) == -1:
                pass


# In[ ]:


class TriangleWave():
    
    def __init__(self, interval=0, fine=0):
        self.name = "SineWave"
        
        self.interval = Parameter(interval, self, 0, 12, name="interval", controllable=True)
        self.fine = Parameter(fine, self, 0, 100,  name="fine", controllable=True)
        self.wave_data = Parameter(None, self, -32768, 32767, "wave_data")
        self.freq = Parameter(0, self, 0.0, None, "freq")
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
        
        for i in range(128):
            freq = self._PITCH * np.power(2, (self.interval.get(i)+i-69)/12)
            freq = freq * np.power(2, self.fine.get(i)/100)
            self.freq.fix(freq, i)
        
        
    def standby(self, synth, pitch=440, rate=44100, bufsize=500):
        self.parent = synth
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
    
    def play(self):
        self._sine()
        
    
    def _sine(self):
        wave_data = []
        offset = self.parent.offset
        vel = self.parent.velocity
        freq = self.freq
        
        for i in range(128):
            if offset.get(i) != -1:
                factor = float(freq.get(i)) * (np.pi*2) / self._RATE
                wave = scipy.signal.sawtooth(np.arange(offset.get(i), offset.get(i)+self._BUF_SIZE) * factor) * 32767/127 * vel.get(i)
                self.parent.wave_data.fix(wave, i)
            elif offset.get(i) == -1:
                pass

