#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from scipy import signal
from synth import *


# In[2]:


class PitchShifter(object):
    
    def __init__(self, interval=0, fine=0):
        self.interval = 0
        self.fine = 0
    
    def standby(self, synth):
        self.parent = synth
        self._BUF_SIZE = self.parent._BUF_SIZE
        self._RATE = self.parent._RATE
        self._PITCH = self.parent._PITCH
    
    def play(self):
        pass


# In[ ]:


class Lowpass(object):
    
    def __init__(self, fp=0, fs=0, gp=3, gs=20):
        self.fp = fp
        self.fs = fs
        self.gp = gp
        self.gs = gs
        self.fn = 44100 / 2
        self.wp = Parameter(self.fp/self.fn, self, name="wp", controllable=True)
        self.ws = Parameter(self.fs/self.fn, self, name="ws", controllable=True)
        
    
    def standby(self, synth):
        self.parent = synth
        self._BUF_SIZE = self.parent._BUF_SIZE
        self._RATE = self.parent._RATE
        self._PITCH = self.parent._PITCH
    
    def play(self): 
        self._effect()
    
    def _effect(self):
        for i in range(128):
            if self.parent.offset.get(i) >= 0:
                # エフェクト記述
                #print(self.parent.wave_data.get(i))
                #print(self.wp.get(i))
                N, Wn = signal.buttord(self.wp.get(i), self.ws.get(i), self.gp, self.gs)
                self.b, self.a = signal.butter(N, Wn, "low")
                wave = signal.filtfilt(self.b, self.a, self.parent.wave_data.get(i))
                #print(wave)
                # FX後の波形を保存
                self.parent.wave_data.fix(wave, i)
                
        


# In[ ]:


class LPC(object):
    def __init__(self, a):
        self.a = a
    
    def standby(self, synth):
        self.parent = synth
        self._BUF_SIZE = self.parent._BUF_SIZE
        self._RATE = self.parent._RATE
        self._PITCH = self.parent._PITCH
    
    def play(self):
        self._effect()
    
    def _effect(self):
        for i in range(128):
            if self.parent.note_on.get(i) == 1:
                # エフェクト記述
                #print(self.parent.wave_data.get(i))
                wave = signal.lfilter([1.0], self.a, self.parent.wave_data.get(i))
                #print(wave)
                # FX後の波形を保存
                self.parent.wave_data.fix(wave/10., i)
                
        

