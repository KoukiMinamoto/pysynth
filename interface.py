#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import copy
import pretty_midi
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
    
    def standby(self, synth):
        # 親となるSynthクラス
        self.parent = synth
        
        # パラメータの生成
        
        # 臨時的な変数
        self.pre_note_on = [0] * 128
        self.pre_offset = [-1] * 128
        
        # その他情報
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
        
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
                    
                if downs[K_z] == True:
                    self.parent.power = False
                        
            
    def _compute_offset(self):
        for i in range(128):
            if self.pre_note_on[i] == 0 and self.parent.note_on.get(i) == 1:
                self.parent.offset.fix(0, i)
                self.parent.R_flag.fix(False, i)
            elif self.pre_note_on[i] == 1 and self.parent.note_on.get(i) == 1:
                self.parent.offset.fix(self.parent.pre_offset.get(i)+self._BUF_SIZE, i)
            elif self.pre_note_on[i] == 1 and self.parent.note_on.get(i) == 0:
                self.parent.offset.fix(self.parent.pre_offset.get(i)+self._BUF_SIZE, i)
                self.parent.R_flag.fix(True, i)
            elif self.pre_note_on[i] == 0 and self.parent.note_on.get(i) == 0 and self.parent.R_flag.get(i) == True:
                self.parent.offset.fix(self.parent.pre_offset.get(i)+self._BUF_SIZE, i)
        
        self.pre_note_on = copy.deepcopy(self.parent.note_on.getall())
        for i in range(128):
            self.parent.pre_offset.fix(self.parent.offset.get(i), i)
                
        


# In[ ]:


class FromMidiFile():
    def __init__(self, midifile=""):
        self.name = "FromMidiFile"
        
        self.midi_data = pretty_midi.PrettyMIDI(midifile)
        self.midi_tracks = self.midi_data.instruments
        self.notes = self.midi_tracks[0].notes
        
    def standby(self, synth):
        self.parent = synth
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
        
        self.piano_roll = self.midi_data.get_piano_roll(fs=self._RATE/self._BUF_SIZE)
        self.pre_note_on = [0] * 128
        self.dtime = self._BUF_SIZE / self._RATE
        self.frame = 0
    
    def play(self):
        
        for i in range(128):
            vel = self.piano_roll[i][self.frame]
            if vel > 0.0:
                self.parent.note_on.fix(1, i)
                self.parent.velocity.fix(vel, i)
            elif vel <= 0.0:
                self.parent.note_on.fix(0, i)
                #self.parent.velocity.fix(0., i)
                
        self.frame = self.frame + 1
        if self.frame == self.piano_roll[0].size:
            self.parent.power = False
        
        self._compute_offset()
        
    def _compute_offset(self):
        for i in range(128):
            if self.pre_note_on[i] == 0 and self.parent.note_on.get(i) == 1:
                self.parent.offset.fix(0, i)
                self.parent.R_flag.fix(False, i)
            elif self.pre_note_on[i] == 1 and self.parent.note_on.get(i) == 1:
                self.parent.offset.fix(self.parent.pre_offset.get(i)+self._BUF_SIZE, i)
            elif self.pre_note_on[i] == 1 and self.parent.note_on.get(i) == 0:
                self.parent.offset.fix(self.parent.pre_offset.get(i)+self._BUF_SIZE, i)
                self.parent.R_flag.fix(True, i)
            elif self.pre_note_on[i] == 0 and self.parent.note_on.get(i) == 0 and self.parent.R_flag.get(i) == True:
                self.parent.offset.fix(self.parent.pre_offset.get(i)+self._BUF_SIZE, i)
        
        self.pre_note_on = copy.deepcopy(self.parent.note_on.getall())
        for i in range(128):
            self.parent.pre_offset.fix(self.parent.offset.get(i), i)

