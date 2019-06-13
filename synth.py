#!/usr/bin/env python
# coding: utf-8

# In[3]:


import numpy as np
import pyaudio
import threading
import pygame
from pygame.locals import *
import time
from error import *
import sys


# In[5]:


class Series():
    """ * モジュールの直列接続をするクラス *
        args:
            + pitch=440 : チューニングピッチ
            + rate=44100 : サンプリングレート
            + bufsize=500 : バッファサイズ
    """
    
    _PITCH = 440
    _RATE = 44100
    _BUF_SIZE = 500
    _PGKEY2KEY = {K_a:'a', K_w:'w', K_s:'s' , K_e:'e', K_d:'d', K_f:'f', K_t:'t', K_g:'g', K_y:'y', K_h:'h', K_u:'u', K_j:'j', K_k:'k'}
    _KEY2MIDI = {"a":60, "w":61, "s":62, "e":63, "d":64, "f":65, "t":66, "g":67, "y":68, "h":69, "u":70, "j":71, "k":72}
    _PGKEY = [K_a, K_w, K_s, K_e, K_d, K_f, K_t, K_g, K_y, K_h, K_u, K_j, K_k]
    _SCREEN_SIZE = (640, 480)
    
    def __init__(self, pitch=440, rate=44100, bufsize=500):
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        self.model = []
    
    
    
    def stack(self, module):
        """ * モジュールの追加に使うメソッド *
            モジュールの追加にかんする制約やエラーの検出を行う
            args:
                + module : 追加するモジュール
        """
        self.model.append(module)
        
        return module
 
        
    def completed(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, 
                                    frames_per_buffer=self._BUF_SIZE, rate=self._RATE, output=True)
        
        for module in self.model:
            if module.name == "SineWave":
                module._standby(pitch=self._PITCH, rate=self._RATE, bufsize=self._BUF_SIZE)
            elif module.name == "SquareWave":
                module._standby(pitch=self._PITCH, rate=self._RATE, bufsize=self._BUF_SIZE)
            elif module.name == "MidiFromPCkey":
                module._standby(pitch=self._PITCH, rate=self._RATE, bufsize=self._BUF_SIZE)
            elif module.name == "SimpleAmp":
                module._standby(stream=self.stream, pitch=self._PITCH, rate=self._RATE, bufsize=self._BUF_SIZE)
            elif module.name == "TriangleWave":
                module._standby(pitch=self._PITCH, rate=self._RATE, bufsize=self._BUF_SIZE)
            elif module.name == "Cabinet":
                module._standby(pitch=self._PITCH, rate=self._RATE, bufsize=self._BUF_SIZE)
        
    def play(self):
        """出力された音声データのみ取得するメソッド"""
        while True:
            start = time.time()
            for module in self.model:
                if module.name == "SineWave":
                    self.wave = module._play(self.freqs, self.offsets, self.amp, self._BUF_SIZE)
                elif module.name == "TriangleWave":
                    self.wave = module._play(self.freqs, self.offsets, self.amp, self._BUF_SIZE)
                elif module.name == "SquareWave":
                    self.wave = module._play(self.freqs, self.offsets, self.amp, self._BUF_SIZE)    
                elif module.name == "MidiFromPCkey":
                    self.freqs, self.offsets, self.amp = module._play()
                elif module.name == "SimpleAmp":
                    module._play(self.wave)
                elif module.name == "Cabinet":
                    self.wave = module._play(self.freqs, self.offsets, self.amp, self._BUF_SIZE)
            print("time: ", time.time()-start)


# In[7]:


class Cabinet():
    def __init__(self, modules, ratio, pitch=440, rate=44100, bufsize=500):
        # リストサイズに関するエラー検出
        if len(modules) != len(ratio):
            raise NotMatchListSize("Number of module and length of ratio list must be same size.")
        if len(modules) <= 1 or len(ratio) <= 1:
            raise NotMatchListSize("List size must be larger than 1.")
            
        self.name = "Cabinet"
        self.modules = modules
        self.ratio = ratio
        self.ratio_sum = sum(ratio)
        
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        
    def _standby(self, pitch=440, rate=44100, bufsize=500):
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        
        for module in self.modules:
            if module.name == "SineWave":
                module._standby(pitch=self._PITCH, rate=self._RATE, bufsize=self._BUF_SIZE)
            elif module.name == "TriangleWave":
                module._standby(pitch=self._PITCH, rate=self._RATE, bufsize=self._BUF_SIZE)
            elif module.name == "SquareWave":
                module._standby(pitch=self._PITCH, rate=self._RATE, bufsize=self._BUF_SIZE)
        return [self.name]
    
    def _play(self, freq, offsets, amp, length):
        self.wave = np.zeros(length, dtype=np.float32)
        
        for i in range(len(self.modules)):
            if self.modules[i].name == "SineWave":
                self.wave = self.wave + (self.ratio[i]/self.ratio_sum) * self.modules[i]._play(freq, offsets, amp, length)
            elif self.modules[i].name == "TriangleWave":
                self.wave = self.wave + (self.ratio[i]/self.ratio_sum) * self.modules[i]._play(freq, offsets, amp, length)
            elif self.modules[i].name == "SquareWave":
                self.wave = self.wave + (self.ratio[i]/self.ratio_sum) * self.modules[i]._play(freq, offsets, amp, length)
        
        out = self.wave
        
        return out


# In[1]:


class Parameter():
    
    def __init__(self, ini_val):
        self.values = [ini_val] * 128
        self.control = Env(A=0., D=0., S=1., R=0., ini_val=ini_val, rang=1.)
        
    def setval(self, new_val, num=-1):
        if num == -1:
            self.values = [new_val] * 128
        else:
            self.values[num] = newval
    
    def getval(self):
        return self.values
    
    def update(self):
        self.values = self.control._update(self.values)
        


# In[ ]:




