#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pyaudio
import threading
import matplotlib.pyplot as plt
import pygame
from pygame.locals import *
import time


# In[2]:


class SimpleSynth():
    """シンセサイザーです。"""
    PITCH = 440
    RATE = 44100
    LEN = 500
    BUF_SIZE = 500
    KEY_FREQ = {"a":60, "w":61, "s":62, "e":63, "d":64, "f":65, "t":66, "g":67, "y":68, "h":69, "u":70, "j":71, "k":72}
    SCREEN_SIZE = (640, 480)
    
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(self.SCREEN_SIZE)
        pygame.key.set_repeat(5, int(1000/self.BUF_SIZE))
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, 
                                    frames_per_buffer=self.BUF_SIZE, rate=self.RATE, output=True)
    
    # MIDIノートを周波数に変換する関数
    def _midi2freq(self, note_num):
        freq = self.PITCH * np.power(2, (note_num-69)/12)
        return freq
    
    #指定周波数でサイン波を生成する
    def sine(self, frequency, length, offset=0):
        length = int(length)
        factor = float(frequency) * (np.pi*2)/self.RATE
        return np.sin(np.arange(offset, offset+length) * factor)
    
    #オーディオ鳴らす
    def play_tone(self, frequency=440, length=44100, offset=0):
        
        chunks = []
        chunks.append(self.sine(frequency, length, offset))
        chunk = np.concatenate(chunks) * 0.25
        self.stream.write(chunk.astype(np.float32).tostring())
        
        #self.stream.close()
        #self.p.terminate()
    
    #シンセサイザーとして使う
    def play_synth(self):
        pre_key = None
        offset = 0
        pygame.display.update()
        while True:
            start_time = time.time()
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    down_keys = pygame.key.get_pressed()
                    if event.key == K_a:
                        freq = self._midi2freq(self.KEY_FREQ['a'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_a
                    elif event.key == K_w:
                        freq = self._midi2freq(self.KEY_FREQ['w'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_w
                    elif event.key == K_s:
                        freq = self._midi2freq(self.KEY_FREQ['s'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_s
                    elif event.key == K_e:
                        freq = self._midi2freq(self.KEY_FREQ['e'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_e
                    elif event.key == K_d:
                        freq = self._midi2freq(self.KEY_FREQ['d'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_d
                    elif event.key == K_f:
                        freq = self._midi2freq(self.KEY_FREQ['f'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_f
                    elif event.key == K_t:
                        freq = self._midi2freq(self.KEY_FREQ['t'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_t
                    elif event.key == K_g:
                        freq = self._midi2freq(self.KEY_FREQ['g'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_g
                    elif event.key == K_y:
                        freq = self._midi2freq(self.KEY_FREQ['y'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_y
                    elif event.key == K_h:
                        freq = self._midi2freq(self.KEY_FREQ['h'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_h
                    elif event.key == K_u:
                        freq = self._midi2freq(self.KEY_FREQ['u'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_u
                    elif event.key == K_j:
                        freq = self._midi2freq(self.KEY_FREQ['j'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_j
                    elif event.key == K_k:
                        freq = self._midi2freq(self.KEY_FREQ['k'])
                        self.play_tone(frequency=freq, length=self.LEN, offset=offset)
                        if event.key == pre_key:
                            offset = offset + self.BUF_SIZE
                        elif event.key != pre_key:
                            offset = 0
                        pre_key = K_k
            
            end_time = time.time()-start_time
            print(end_time)
           
            


# In[ ]:


if __name__ == '__main__':
    synth = SimpleSynth()
    #synth.play_tone()
    synth.play_synth()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




