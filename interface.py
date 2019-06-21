#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import copy
import pyaudio
import threading
import matplotlib.pyplot as plt
import pygame
from pygame.locals import *
from synth import *


# In[ ]:


class MidiFromPCkey():
    """ * PCキーから入力をMIDI信号に変換し周波数とオフセットを返します。*
        + _init(): 初期化処理を行うメソッド
        + _run() : メインの処理
        + _play(): PCキーを周波数とオフセットに変換します
    """
    
    def __init__(self):
        self.name = "MidiFromPCkey"
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
        self._PGKEY2KEY = {K_a:'a', K_w:'w', K_s:'s' , K_e:'e', K_d:'d', K_f:'f', K_t:'t', K_g:'g', K_y:'y', K_h:'h', K_u:'u', K_j:'j', K_k:'k'}
        self._KEY2MIDI = {"a":60, "w":61, "s":62, "e":63, "d":64, "f":65, "t":66, "g":67, "y":68, "h":69, "u":70, "j":71, "k":72}
        self._PGKEY = [K_a, K_w, K_s, K_e, K_d, K_f, K_t, K_g, K_y, K_h, K_u, K_j, K_k]
        self._SCREEN_SIZE = (640, 480)
    
    def standby(self, synth, pitch=440, rate=44100, bufsize=500):
        # 親となるSynthクラス
        self.parent = synth
        
        # パラメータの生成
        
        # 臨時的な変数
        self.pre_note_on = [0] * 128
        self.pre_offset = [-1] * 128
        
        # その他情報
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        
        # pygameの初期設定
        pygame.init()
        screen = pygame.display.set_mode(self._SCREEN_SIZE)
        pygame.key.set_repeat(1, 1)
    
    def play(self):
        """ * メインの処理を実行するメソッド *
            -return:
                Note-ON/OFF: 各ノートナンバーに対して、キーのON/OFFを1/0で返します。 shape=(128,1)
                Velocity: 各ノートナンバーに対応するベロシティの大きさを返します。 shape=(128, 1)
        """
        # PCkeyに対応したMIDI信号を生成し、note_onとvelocityを更新します。
        self._PCkey2midi()
        self._compute_offset()
        
        
    
    def _PCkey2midi(self):
        # pygame内のイベントを拾う
        for event in pygame.event.get():
            # 押されているキーを取得(ディクショナリ型) ex)downs[K_a] = True
            downs = pygame.key.get_pressed()
                
            midi_notes = []# MIDIノート形式で格納
            long_press_index = []# 長押しされているキーのインデックス(offsetの計算とかに使う)
            
            if event.type == QUIT:# 閉じるボタンが押されたら終了
                pygame.quit()     
                
            for key in self._PGKEY:
                if downs[key] == True:
                    # pygame仕様のキーをPCキーボード仕様に変換後、MIDIノートに変換しリストに追加
                    note_num = self._KEY2MIDI[self._PGKEY2KEY[key]]
                    self.parent.note_on.fix(1, note_num=note_num)
                    self.parent.velocity.fix(127, note_num=note_num)
                elif downs[key] == False:
                    note_num = self._KEY2MIDI[self._PGKEY2KEY[key]]
                    self.parent.note_on.fix(0, note_num=note_num)
                    #self.parent.velocity.fix(0, note_num=note_num)
                    
                elif downs[K_z] == True:
                    self.parent.power = False
                        
            
                        
                        
    def _compute_offset(self):
        for i in range(128):
            if self.pre_note_on[i] == 0 and self.parent.note_on.get(i) == 1:
                self.parent.offset.fix(0, i)
                self.parent.R_flag.fix(False, i)
            elif self.pre_note_on[i] == 1 and self.parent.note_on.get(i) == 1:
                self.parent.offset.fix(self.pre_offset[i]+self._BUF_SIZE, i)
            elif self.pre_note_on[i] == 1 and self.parent.note_on.get(i) == 0:
                self.parent.offset.fix(self.pre_offset[i]+self._BUF_SIZE, i)
                self.parent.R_flag.fix(True, i)
            elif self.pre_note_on[i] == 0 and self.parent.note_on.get(i) == 0 and self.parent.R_flag.get(i) == True:
                self.parent.offset.fix(self.pre_offset[i]+self._BUF_SIZE, i)
        
        self.pre_note_on = copy.deepcopy(self.parent.note_on.getall())
        self.pre_offset = copy.deepcopy(self.parent.offset.getall())
                
        


# In[2]:


class MidiFromPCkey_deprecated():
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
        """ * メインの処理を実行するメソッド *
            -return:
                Note-ON/OFF: 各ノートナンバーに対して、キーのON/OFFを1/0で返します。shape=(128,1)
                
        
        """
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
                    print("bufsize: ", self._BUF_SIZE)
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
        print(self.freqs, self.offsets)    
        return self.freqs, self.offsets, 0.25

