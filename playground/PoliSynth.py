#!/usr/bin/env python
# coding: utf-8

# # PoliSynth -ポリフォニック・シンセサイザー-
# ***
# ## 概要
# * 2音のポリフォニック・シンセサイザーです。
# 
# ## 使い方
# 1. ディペンデンシーのモジュールをインストールします。
#     ```
#     \$ pip3 install numpy
#     \$ pip3 install pyaudio
#     \$ pip3 install pygame
#     ```  
# </br>
# 2. SimpleSynthをインスタンス化します。
# 3. SimpleSynth.play_synth()メソッドでPCのキーボード入力からMIDI信号に変換して音がなります。

# In[1]:


import numpy as np
import pyaudio
import threading
import matplotlib.pyplot as plt
import pygame
from pygame.locals import *

class SimpleSynth():
    """シンセサイザーです。"""
    PITCH = 440
    RATE = 44100
    LEN = 500
    BUF_SIZE = 500
    PGKEY2KEY = {K_a:'a', K_w:'w', K_s:'s' , K_e:'e', K_d:'d', K_f:'f', K_t:'t', K_g:'g', K_y:'y', K_h:'h', K_u:'u', K_j:'j', K_k:'k'}
    KEY2MIDI = {"a":60, "w":61, "s":62, "e":63, "d":64, "f":65, "t":66, "g":67, "y":68, "h":69, "u":70, "j":71, "k":72}
    PGKEY = [K_a, K_w, K_s, K_e, K_d, K_f, K_t, K_g, K_y, K_h, K_u, K_j, K_k]
    SCREEN_SIZE = (640, 480)
    
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(self.SCREEN_SIZE)
        pygame.key.set_repeat(5, int(1000/self.BUF_SIZE))
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, 
                                    frames_per_buffer=self.BUF_SIZE, rate=self.RATE, output=True)
    
    # MIDIノートを周波数に変換する関数
    def _midi2freq(self, midi_notes=[]):
        freq = []
        for note in midi_notes:
            freq.append(self.PITCH * np.power(2, (note-69)/12))
        return freq
    
    #指定周波数でサイン波を生成する
    def sine(self, frequency, length, offset=0):
        length = int(length)
        frequency = np.squeeze(frequency)
        factor = float(frequency) * (np.pi*2)/self.RATE
        return np.sin(np.arange(offset, offset+length) * factor)
    
    #オーディオ鳴らす
    def play_tone(self, frequency=[440], length=44100, offset=[0]):
        if len(frequency) <= 0:
            pass
        elif len(frequency) > 0:
            chunks = []
            chunks.append(self.sine(frequency[0], length, offset[0]))
            chunk = np.concatenate(chunks) * 0.25
            for i in range(len(frequency)-1):
                chunks = []
                chunks.append(self.sine(frequency[i+1], length, offset[i]))
                chunk = chunk + (np.concatenate(chunks) * 0.25)
        
            self.stream.write(chunk.astype(np.float32).tostring())
        
        #self.stream.close()
        #self.p.terminate()
    
    #シンセサイザーとして使う
    def play_synth(self):
        pre_keys = [None, None, None]
        offsets = [0,0,0]
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                downs = pygame.key.get_pressed()
                midi_notes = []
                freq = []
                long_press_index = []
                if event.type == KEYDOWN:
                    for key in self.PGKEY:
                        if downs[key] == True:
                            midi_notes.append(self.KEY2MIDI[self.PGKEY2KEY[key]])
                        else:
                            pass
                else:
                    pass
                print("midi_notes = ", midi_notes)
                freq.append(self._midi2freq(midi_notes))
                freq = np.concatenate(freq)
                print("freq = ", freq)
                self.play_tone(frequency=freq, length=self.LEN, offset=offsets)
                for prekey in pre_keys:
                    if midi_notes.count(prekey) > 0:
                        index = midi_notes.index(prekey)
                        long_press_index.append(index)
                        offsets[index] = offsets[index] + self.BUF_SIZE
                    else:
                        reset_keys = []
                        for i in range(len(offsets)):
                            if long_press_index.count(i) == 0:
                                reset_keys.append(i)
                            for key in reset_keys:
                                offsets[key] = 0
                print("offset = ", offsets)              
                pre_keys = midi_notes


# In[ ]:


if __name__ == '__main__':
    synth = SimpleSynth()
    #synth.play_tone()
    synth.play_synth()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




