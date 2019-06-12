#!/usr/bin/env python
# coding: utf-8

# In[14]:


import numpy as np
import pyaudio
import threading
import matplotlib.pyplot as plt
import pygame
from pygame.locals import *


# In[2]:


class MidiFromPCkey():
    """ * PCキーから入力をMIDI信号に変換し周波数とオフセットを返します。*
        + _init(): 初期化処理を行うメソッド
        + _run() : メインの処理
        + _play(): PCキーを周波数とオフセットに変換します
    """
    
    def __init__(self):
        self.name = "MidiFromPCkey"
        self.val = None
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
        self._POLI = 3
        self._PGKEY2KEY = {K_a:'a', K_w:'w', K_s:'s' , K_e:'e', K_d:'d', K_f:'f', K_t:'t', K_g:'g', K_y:'y', K_h:'h', K_u:'u', K_j:'j', K_k:'k'}
        self._KEY2MIDI = {"a":60, "w":61, "s":62, "e":63, "d":64, "f":65, "t":66, "g":67, "y":68, "h":69, "u":70, "j":71, "k":72}
        self._PGKEY = [K_a, K_w, K_s, K_e, K_d, K_f, K_t, K_g, K_y, K_h, K_u, K_j, K_k]
        self._SCREEN_SIZE = (640, 480)
    
    def _standby(self, pitch=440, rate=44100, bufsize=500):
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        self.offsets = [0,0,0,0,0,0,0,0]
        self.pre_keys = []
        
        pygame.init()
        screen = pygame.display.set_mode(self._SCREEN_SIZE)
        pygame.key.set_repeat(1, 1)
        
        return [self.name]
        
    def _play(self):
        return self._PCkey2freq()
        # return f, os, 0.25
        
    def _midi2freq(self, midi_notes):
        freqs = []
        
        for note in midi_notes:
            freqs.append(self._PITCH * np.power(2, (note-69)/12))
            
        return freqs
    
    def _PCkey2freq(self):
        # ここの配列のサイズを変えると同時発音数が変わる ex)要素数3→3音ポリ
        # pygameのウィンドウのアップデート
        # pygame内のイベントを拾う
        for event in pygame.event.get():
            # 押されているキーを取得(ディクショナリ型) ex)downs[K_a] = True
            downs = pygame.key.get_pressed()
                
            midi_notes = []# MIDIノート形式で格納
            long_press_index = []# 長押しされているキーのインデックス(offsetの計算とかに使う)
            
            if event.type == QUIT:# 閉じるボタンが押されたら終了
                pygame.quit()     
                
            # 拾ったイベントがキーの押下だった場合
            if event.type == KEYDOWN:
                # 鍵盤に対応したキーが押されている場合
                for key in self._PGKEY:
                    if downs[key] == True:
                        # pygame仕様のキーをPCキーボード仕様に変換後、MIDIノートに変換しリストに追加
                        midi_notes.append(self._KEY2MIDI[self._PGKEY2KEY[key]])
                        
                    else:
                        pass
            else:
                pass
            # MIDIノートを周波数に変換
            self.freqs = self._midi2freq(midi_notes)
                
            # 一つ前のループで押下されていたキーに対して
            for prekey in self.pre_keys:
                # 今回のループでも押下されている場合
                if midi_notes.count(prekey) > 0:
                    # 押下されているキーのmidi_notes上でのインデックスを探索し
                    index = midi_notes.index(prekey)
                    # 長押しされているキーとして、そのインデックスを格納。
                    long_press_index.append(index)
                    # そのインデックスに対応したoffsetにBUF_SIZE分のオフセットを追加
                    self.offsets[index] = self.offsets[index] + self._BUF_SIZE
                else:
                    reset_keys = []# offsetにリセットをかけるべきキーに対応したインデックスを格納
                        
                    for i in range(len(self.offsets)):
                        # 長押しが終わった(=オフセットにリセットをかけるべき)キーに対して
                        if long_press_index.count(i) == 0:
                            # そのキーに対応したインデックスを追加
                            reset_keys.append(i)
                        # リセットをかけるべきoffsetのインデックスに対して
                        for key in reset_keys:
                            # リセットをかける
                            self.offsets[key] = 0
                            
            # 現在押されているMIDIノートをpre_keysに更新
            self.pre_keys = midi_notes
            #print(self.freqs, self.offsets, midi_notes)
        # print(self.freqs, self.offsets)    
        return self.freqs, self.offsets, 0.25


# In[ ]:




