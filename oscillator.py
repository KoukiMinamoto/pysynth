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
        
        
    def standby(self, synth):
        self.parent = synth
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
    
    def play(self):
        self._sine()
        
    
    def _sine(self):
        wave_data = []
        offset = self.parent.offset
        vel = self.parent.velocity
        
        for i in range(128):
            freq = self._PITCH * np.power(2, (self.interval.get(i)+i-69)/12)
            freq = freq * np.power(2, self.fine.get(i)/100)
            self.freq.fix(freq, i)
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
        
        
    def standby(self, synth):
        self.parent = synth
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
    
    def play(self):
        self._sine()
        
    
    def _sine(self):
        wave_data = []
        offset = self.parent.offset
        vel = self.parent.velocity
        for i in range(128):
            freq = self._PITCH * np.power(2, (self.interval.get(i)+i-69)/12)
            freq = freq * np.power(2, self.fine.get(i)/100)
            self.freq.fix(freq, i)
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
        
        
    def standby(self, synth):
        self.parent = synth
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
    
    def play(self):
        self._sine()
        
    
    def _sine(self):
        wave_data = []
        offset = self.parent.offset
        vel = self.parent.velocity
        for i in range(128):
            freq = self._PITCH * np.power(2, (self.interval.get(i)+i-69)/12)
            freq = freq * np.power(2, self.fine.get(i)/100)
            self.freq.fix(freq, i)
        freq = self.freq
        
        for i in range(128):
            if offset.get(i) != -1:
                factor = float(freq.get(i)) * (np.pi*2) / self._RATE
                wave = scipy.signal.sawtooth(np.arange(offset.get(i), offset.get(i)+self._BUF_SIZE) * factor) * 32767/127 * vel.get(i)
                self.parent.wave_data.fix(wave, i)
            elif offset.get(i) == -1:
                pass


# In[ ]:


class ToufuWave():
    """ * サイン波を生成するモジュール *
        -args: 
            Note_ON/OFF: list(128, 1)
            Velocity:    list(128, 1)
            
        -return: wave_data: list(128, BUFSIZE)
    """
    def __init__(self, interval=0, fine=0):
        self.name = "SineWave"
        
        self.interval = Parameter(interval, self, 0, None, name="interval", controllable=True)
        self.fine = Parameter(fine, self, 0, None,  name="fine", controllable=True)
        self.wave_data = Parameter(None, self, -32768, 32767, "wave_data")
        self.freq = Parameter(0, self, 0.0, None, "freq")
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
        
        
    def standby(self, synth):
        self.parent = synth
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
        
        self.fade_W = int(self._BUF_SIZE/8)
        self.fade = Parameter(np.zeros(self.fade_W), self, None, None, "fade")
        self.coeff_fade = np.linspace(1, 0, self.fade_W)
        self.coeff_wave = np.linspace(0, 1, self.fade_W)
        self.coeff_wave = np.concatenate([self.coeff_wave, np.ones(self._BUF_SIZE-self.fade_W)])
    
    def play(self):
        self._sine()
        
    
    def _sine(self):
        wave_data = []
        offset = self.parent.offset
        vel = self.parent.velocity
        
        for i in range(128):
            freq = self._PITCH * np.power(2, (self.interval.get(i)+i-69)/12)
            freq = freq * np.power(2, self.fine.get(i)/100)
            self.freq.fix(freq, i)
        freq = self.freq
        
        for i in range(128):
            if offset.get(i) != -1:
                factor = float(freq.get(i)) * (np.pi*2) / self._RATE
                wave = np.sin(np.arange(offset.get(i), offset.get(i)+self._BUF_SIZE) * factor) * 32767/127 * vel.get(i)
                wave = wave + np.sin(2.1 * np.arange(offset.get(i), offset.get(i)+self._BUF_SIZE) * factor) * 32767/127 * vel.get(i)
                wave = wave + np.sin(3.0 * np.arange(offset.get(i), offset.get(i)+self._BUF_SIZE) * factor) * 32767/127 * vel.get(i)
                wave = 1/3 * wave
                self.fade.fix(self.coeff_fade * self.fade.get(i), i)
                self.fade.fix(np.concatenate([self.fade.get(i), np.zeros(self._BUF_SIZE-self.fade_W)]), i)
                wave = self.coeff_wave * wave
                wave = wave + self.fade.get(i)
                self.parent.wave_data.fix(wave, i)
                
                wave = np.sin(np.arange(offset.get(i)+self._BUF_SIZE, offset.get(i)+self._BUF_SIZE+self.fade_W) * factor) * 32767/127 * vel.get(i)
                wave = wave + np.sin(2.1 * np.arange(offset.get(i)+self._BUF_SIZE, offset.get(i)+self._BUF_SIZE+self.fade_W) * factor) * 32767/127 * vel.get(i)
                wave = wave + np.sin(3.0 * np.arange(offset.get(i)+self._BUF_SIZE, offset.get(i)+self._BUF_SIZE+self.fade_W) * factor) * 32767/127 * vel.get(i)
                wave = 1/3 * wave
                self.fade.fix(wave, i)
                
            elif offset.get(i) == -1:
                pass


# In[ ]:


class PulseWave():
    """ * サイン波を生成するモジュール *
        -args: 
            Note_ON/OFF: list(128, 1)
            Velocity:    list(128, 1)
            
        -return: wave_data: list(128, BUFSIZE)
    """
    def __init__(self, interval=0, fine=0):
        self.name = "PalseWave"
        
        self.interval = Parameter(interval, self, 0, 12, name="interval", controllable=True)
        self.fine = Parameter(fine, self, 0, 100,  name="fine", controllable=True)
        self.wave_data = Parameter(None, self, -32768, 32767, "wave_data")
        self.freq = Parameter(0, self, 0.0, None, "freq")
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
        
        
    def standby(self, synth):
        self.parent = synth
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
    
    def play(self):
        self._sine()
        
    
    def _sine(self):
        wave_data = []
        offset = self.parent.offset
        vel = self.parent.velocity
        
        # 周波数の計算(書き換えない)
        for i in range(128):
            freq = self._PITCH * np.power(2, (self.interval.get(i)+i-69)/12)
            freq = freq * np.power(2, self.fine.get(i)/100)
            self.freq.fix(freq, i)
        freq = self.freq
        
        # 波形の形成    
        for i in range(128):
            if offset.get(i) != -1:
                wave = np.zeros(self._BUF_SIZE)
                period = 1. / float(freq.get(i)) * self._RATE
                index = period - offset.get(i) % period
                while(1):
                    wave[int(index)] = 127 * vel.get(i)
                    index = index + period
                    if index >= self._BUF_SIZE:
                        break
                self.parent.wave_data.fix(wave, i)
            elif offset.get(i) == -1:
                pass 


# In[ ]:




