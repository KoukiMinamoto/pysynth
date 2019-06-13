#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import scipy 
import synth


# In[ ]:


class Envelope_old():
    def __init__(self, A=0.1, D=0.1, S=0.8, R=1.0):
        
        # ADSRの値保持用
        self.A = A
        self.D = D
        self.S = S
        self.R = R
        
        
        self.classes = []
        self.assigns = {}
        # 前回のEnv参照時のノートオンの状態
        self.pre_note_on = [0] * 128
        self.pre_values = {}
        # 各パラメータの持続フレーム数を保存して、ADSRのどの範囲かを判断する用
        self.adsr = {}
        self.pre_attack_idx = []
        self.pre_sustain_idx = []
        self.pre_release_idx = []
        # 初期値
        self.inival = {}
        # 適応範囲
        self.rang = {}
        self.flag_R = False
        
        # 諸情報
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
    
    def assign(self, param, ini_value=0, rang=1.0):
        '''
            +args:
                -param: [アサインする変数をもつクラス, "アサインする変数の名前", アサインする変数(リスト)のサイズ]
        '''
        
        self.adsr[param[0]][param[1]] = [0] * param[2]
        self.inival[param[0]][param[1]] = [ini_value]
        self.rang[param[0]][param[1]] = [rang]
        
        
        
    def _standby(self, interface, pitch=440, rate=44100, bufsize=500):
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        # インターフェースで返されるnote_onをトリガーとして使用するため
        self.interface = interface
    
    def _update(self, module, name, values):
        
        attack_note_idx = []
        sustain_note_idx = []
        release_note_idx= []
        
        note_on = self.interface.note_on
        velocities = self.interface.velocities
        
        # どのキーがAttackなのかRleaseなのかとかを判断
        for i in range(len(note_on)):
            for j in range(len(self.pre_note_on)):
                if note_on[i] != self.pre_note_on[j]:
                    if note_on[i] == 1:
                        attack_note_idx.append(i)
                    elif note_on[i] == 0:
                        release_note_idx.append(i)
                        self.flag_R = True
                elif note_on[i] == self.pre_note_on:
                    if note_on[i] == 1:
                        sustain_note_idx.append(i)
                    elif note_on[i] == 0:
                        if self.pre_release_idx.count(i) > 0:
                            release_note_idx.append(i)
                            
        self.pre_note_on = note_on
                        
                
        # valuesがampの場合
        if len(values) == len(note_on):
            pass
        else:
            
        self.flag_R = False
            
    
    def  _adsrmap(self, adsr, vel, preval, inival, rang, flag_R):
        factor = None
        if adsr <= self._RATE * self.A and adsr >= 0:
            factor = ((vel * rang) - inival) / self._RATE * self.A
        elif adsr > self._RATE * self.A and adsr <= self._RATE * (self.A + self.D):
            factor = ((vel * rang) - self.S * (inival * rang)) / (self._RATE * self.D)
        elif adsr > self._RATE * (self.A + self.D) and flag_R != True:
            factor = 1.0
        elif flag_R == True:
            factor (self.S * (vel * rang)) / self._RATE * self.R
        
        return preval * factor
        
        
        
        


# In[ ]:


HOLD


# In[ ]:


class Envelope():
    HOLD_TIME = Parameter(0.0)
    def __init__(self, A=0.0, D=0.0,

