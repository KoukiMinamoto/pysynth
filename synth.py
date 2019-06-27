#!/usr/bin/env python
# coding: utf-8

# In[3]:


import numpy as np
import pyaudio
import threading
import wave
import pygame
from pygame.locals import *
import time
from error import *
import sys
from interface import *
from controller import *


# In[ ]:


class Series(object):
    """ * モジュールの直列接続をするクラス *
        args:
            + pitch=440 : チューニングピッチ
            + rate=44100 : サンプリングレート
            + bufsize=500 : バッファサイズ
    """
    def __init__(self, pitch=440, rate=44100, bufsize=500):
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        self.model = []
        self.controller = []
        self.pre_note_on = [0] * 128
        self.power = True
        self.out_file_name = ""
        self.file_out = False
        self.all_out_data = []
        
        self.note_on = Parameter(0, self, 0, 1, "note_on")
        self.velocity = Parameter(0, self, 0, 127, "velocity")
        self.wave_data = Parameter(np.zeros(self._BUF_SIZE), self, -32768, 32767, "wave_data")
        self.offset = Parameter(-1, self, -1, None, "offset")
        self.pre_offset = Parameter(-1, self, -1, None, "pre_offset")
        self.R_flag = Parameter(False, self, name="R_flag")
        
        
    def implement(self, module):
        module_name = module.__module__
        if module_name != "controller":
            raise InvalidModuleImplement("Can implement modules only from controller.")
        else:
            self.controller.append(module)
            
    def stack(self, module):
        module_name = module.__module__
        class_name = module.__class__.__name__
        
        if len(self.model) == 0:
            if module_name == "interface":
                self.model.append(module)
            else:
                raise InvalidModuleStack("First module must be from interface.")
        elif len(self.model) == 1:
            if module_name == "oscillator" or module_name == "sampler":
                self.model.append(module)
            elif class_name == "cabinet":
                if module.mode == "osc":
                    self.model.append(module)
                else:
                    raise InvalidModuleStack("Cabinet doesn't have oscillator module or sampler module.")
            else:
                raise InvalidModuleStack("Second module must be from oscillator")
        elif len(self.model) >= 2:
            if module_name == "interface":
                raise InvalidModuleStack("Cannot stack interface module twice.")
            elif module_name == "oscillator":
                raise InvalidModuleStack("Cannot stack oscillator module twice.")
            elif class_name == "cabinet":
                if module.mode == "osc":
                    raise InvalidModuleStack("Cabinet has oscillator stack.")
            else:
                self.model.append(module)
        
        
        return module
                
        
    def completed(self):
        last_module = self.model[len(self.model)-1].__module__
        if last_module != "amplifier":
            raise InvalidModuleStack("Amplifier module is NOT stacked at last layer.")
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, 
                                    frames_per_buffer=self._BUF_SIZE, rate=self._RATE, output=True)
        
        for module in self.model:
            module.standby(synth=self)
        for control in self.controller:
            control.standby(synth=self)
            
        print("Your Synth is completed!!")
        print("Structure: ", self.model)
        
        
    def play(self):
        while self.power == True:
            for module in self.model:
                module.play()
                for control in self.controller:
                    control.update(module)
            out_data = np.zeros(self._BUF_SIZE)
            for i in range(128):
                out_data = out_data + self.model[len(self.model)-1].amp.get(i)
            
            for i in range(128):
                self.pre_note_on[i] = self.note_on.get(i)
            
            if self.stream.is_active():
                if self.file_out == True:
                    self.all_out_data.append(out_data.astype(np.int16))
                self.stream.write(out_data.astype(np.int16).tostring())
        
        print("Abandoned your synth.")
        self.abandon()
        
        return True
        
    def abandon(self):
        if self.file_out == True:
            self.all_out_data = np.concatenate(self.all_out_data)
            w = wave.Wave_write(self.out_file_name)
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(self._RATE)
            w.writeframes(self.all_out_data)
            w.close()
            
        pygame.quit()   
        self.stream.close()
        self.p.terminate()
        
            


# In[ ]:


class Cabinet():
    pass


# In[ ]:


class _Cabinet():
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
            elif module.name == "WizavoPCM":
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
            elif self.modules[i].name == "WizavoPCM":
                self.wave = self.wave + (self.ratio[i]/self.ratio_sum) * self.modules[i]._play(freq, offsets, amp, length)
        
        out = self.wave
        
        return out


# In[ ]:


class Parameter():
    
    def __init__(self, value, parent, minval=None, maxval=None, name='', controllable=False):
        self.name = name
        self.values = [value for x in range(128)]
        self.inival = [value for x in range(128)]
        self.parent = parent
        self.minval = minval
        self.maxval = maxval
        self.controllable = controllable
        
        
    def replace(self, value):
        self.values = [value for x in range(128)]
        
    def fix(self, value, note_num, buf_num=None):
        if isinstance(value, np.ndarray):
            self.values[note_num] = np.copy(value)
        else:
            if buf_num != None and isinstance(self.values[0], np.ndarray):
                self.values[note_num][buf_num] = value
            elif buf_num == None:
                self.values[note_num] = value
        
    def get(self, note_num, buf_num=None):
        if buf_num != None:
            return self.values[note_num][buf_num]
        else:
            return self.values[note_num]
    
    def getall(self):
        return self.values
        

