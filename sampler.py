#!/usr/bin/env python
# coding: utf-8

# In[3]:


import wave
import numpy
import pyaudio
import math
import scipy.signal
from synth import *


# In[ ]:


class Sampler():
    """ * サイン波を生成するモジュール *
        -args: 
            Note_ON/OFF: list(128, 1)
            Velocity:    list(128, 1)
            
        -return: wave_data: list(128, BUFSIZE)
    """
    def __init__(self, wavefile, interval=0, fine=0, calibration=True):
        self.name = "Sampler"
        
        self.croma_range = 12
        self.terminate = False
        self.loop = False
        self.wavefile = wavefile
        self.interval = Parameter(interval, self, 0, 12, name="interval", controllable=True)
        self.fine = Parameter(fine, self, 0, 100,  name="fine", controllable=True)
        self.freq = Parameter(0, self, 0.0, None, "freq")
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
        
        self.wr = wave.open(self.wavefile, "rb")
        self.data = self.wr.readframes(self.wr.getnframes())
        self.data = np.frombuffer(self.data, count=self.wr.getnframes(), offset=0, dtype=np.int16)
        
        
    def standby(self, synth):
        self.parent = synth
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
        
        self.out_data = Parameter(0, self, -32768, 32767, name="out_data")
        self.out_data.fix(self.data, 60)
        for i in range(self.croma_range):
            data = self._downsampling(np.power(2, (i+1)/12))
            self.out_data.fix(data, 60+i+1)
            #print(self.out_data.get(60+i+1))
            data = self._upsampling(np.power(2, -(i+1)/12))
            self.out_data.fix(data, 60-(i+1))
            
    
    def play(self):
        wave_data = []
        offset = self.parent.offset
        vel = self.parent.velocity
        
        for i in range(60-self.croma_range, 60+self.croma_range+1):
            if offset.get(i) != -1:
                len_diff = self.out_data.get(i).size - offset.get(i)
                if len_diff <= 0:
                    wave = np.zeros(self._BUF_SIZE)
                elif len_diff < self._BUF_SIZE:
                    wave = vel.get(i)/127 * self.out_data.get(i)[offset.get(i): offset.get(i)+len_diff]
                    for j in range(self._BUF_SIZE - len_diff):
                        wave = np.append(wave, 0.0)
                    self.parent.offset.fix(-1, i)
                else:
                    wave = self.out_data.get(i)[offset.get(i): offset.get(i)+self._BUF_SIZE]
                self.parent.wave_data.fix(wave, i)
                
            elif offset.get(i) == -1:
                pass
                
    def loop(self, pos, length, fade):
        self.loop = True
        self.pos = pos
        self.length = length
        self.fade = fade
        
    def _loop(self):
        pass
        
    def _upsampling(self, rate):
        """
        アップサンプリングを行う．
        入力として，変換レートとデータとサンプリング周波数．
        アップサンプリング後のデータとサンプリング周波数を返す．
        """
        # 補間するサンプル数を決める
        interpolationSampleNum = rate - 1
        
        data = self.data.tolist()

        # FIRフィルタの用意をする
        nyqF = self._RATE/2.0
        cF = (self._RATE/2.0-500.)/nyqF
        taps = 511 
        b = scipy.signal.firwin(taps, cF)

        # 補間処理
        upData = []
        offset = 0
        for i in range(len(data)):
            upData.append(data[i])
            # 1サンプルの後に，interpolationSampleNum分だけ0を追加する
            nsample = ((interpolationSampleNum * i) // 1) - offset
            offset = offset + nsample
            for j in range(int(nsample)):
                upData.append(data[i])

        # フィルタリング
        resultData = scipy.signal.lfilter(b,1,upData)
        return np.array(resultData, dtype=np.int16)
   
    
    def _downsampling(self, rate):
        """
        ダウンサンプリングを行う．
        入力として，変換レートとデータとサンプリング周波数．
        ダウンサンプリング後のデータとサンプリング周波数を返す．
        """
        # 間引くサンプル数を決める
        decimationSampleNum = rate - 1
        
        # FIRフィルタの用意をする
        nyqF = self._RATE/2.0             # 変換後のナイキスト周波数
        cF = (self._RATE/rate/2.0-500.)/nyqF     # カットオフ周波数を設定（変換前のナイキスト周波数より少し下を設定）
        taps = 511                                  # フィルタ係数（奇数じゃないとだめ）
        b = scipy.signal.firwin(taps, cF)           # LPFを用意

        #フィルタリング
        data = scipy.signal.lfilter(b,1,self.data)
        data = data.tolist()

        #間引き処理
        left = 0
        for i in range(len(self.data)):
            try:
                nsample = decimationSampleNum // 1
                left = left + decimationSampleNum % 1
                if left >= 1.0:
                    nsample = nsample + 1
                    left = left - 1
                for j in range(int(nsample)):
                    data.pop(i+1)
            except IndexError:
                pass
        
        print("size: ", len(data))    
        return np.array(data, dtype=np.int16)

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
    

