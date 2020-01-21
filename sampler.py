#!/usr/bin/env python
# coding: utf-8

# In[3]:


import wave
import numpy as np
import pyaudio
import math
import scipy.signal
from scipy import arange, around, array, linspace
from scipy.interpolate import interp1d
from scipy.signal import resample
from synth import *
import numba


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
        self.interval = Parameter(interval, self, 0, None, name="interval", controllable=True)
        self.fine = Parameter(fine, self, 0, None,  name="fine", controllable=True)
        self.freq = Parameter(0, self, 0.0, None, "freq")
        
        self.wr = wave.open(self.wavefile, "rb")
        self.data = self.wr.readframes(self.wr.getnframes())
        print(self.wr.getnframes())
        self.data = np.frombuffer(self.data, count=self.wr.getnframes(), offset=0, dtype=np.int16)
        print(np.shape(self.data))
        
    def standby(self, synth):
        self.parent = synth
        self._PITCH = self.parent._PITCH
        self._RATE = self.parent._RATE
        self._BUF_SIZE = self.parent._BUF_SIZE
        
        self.out_data = Parameter(0, self, -32768, 32767, name="out_data")
        self.out_data.fix(self.data, 60)
        for i in range(self.croma_range):
            data = self.resampling(self.data, np.power(2, (i+1)/12))
            self.out_data.fix(data, 60+i+1)
            data = self.resampling(self.data, np.power(2, -(i+1)/12))
            self.out_data.fix(data, 60-(i+1))
            
    
    def play(self):
        wave_data = np.zeros(self._BUF_SIZE)
        offset = self.parent.offset
        vel = self.parent.velocity
        
        if self.loop == False:
            for i in range(60-self.croma_range, 60+self.croma_range+1):
                if offset.get(i) != -1:
                    len_diff = self.out_data.get(i).size - offset.get(i)
                    if len_diff <= 0:
                        wave = np.zeros(self._BUF_SIZE)
                    elif len_diff < self._BUF_SIZE:
                        wave = vel.get(i)/127 * self.out_data.get(i)[offset.get(i): offset.get(i)+len_diff]
                        for j in range(self._BUF_SIZE - len_diff):
                            wave = np.append(wave, 0.0)
                    else:
                        wave = vel.get(i)/127 * self.out_data.get(i)[offset.get(i): offset.get(i)+self._BUF_SIZE]
                    if self.fine.get(i) != 0:
                                    wave = self.pitch_shift(wave, np.power(2, self.fine.get(i)/100))
                    self.parent.wave_data.fix(wave, i)

                elif offset.get(i) == -1:
                    pass
        else:
            for i in range(60-self.croma_range, 60+self.croma_range+1):
                if self.parent.offset.get(i) != -1:
                    start_pos = (self.out_data.get(i).size * self.pos) - ((self.out_data.get(i).size * self.pos) % self._BUF_SIZE)
                    end_pos = (self.out_data.get(i).size * (self.pos+self.length)) - ((self.out_data.get(i).size * (self.pos+self.length)) % self._BUF_SIZE)
                    fade_pos = end_pos - ((end_pos - start_pos) * self.fade) - (((end_pos - start_pos) * self.fade) % self._BUF_SIZE)
                    prefade_pos = start_pos - ((end_pos - start_pos) * self.fade) - (((end_pos - start_pos) * self.fade) % self._BUF_SIZE)
                    factor = 1.0 / (end_pos - fade_pos + 1)
                        
                    if self.parent.R_flag.get(i) == True:
                        len_diff = self.out_data.get(i).size - self.parent.offset.get(i)
                        if len_diff <= 0:
                            wave = np.zeros(self._BUF_SIZE)
                            self.parent.wave_data.fix(wave, i)
                        elif len_diff < self._BUF_SIZE:
                            wave = vel.get(i)/127 * self.out_data.get(i)[self.parent.offset.get(i): self.parent.offset.get(i)+len_diff]
                            for j in range(self._BUF_SIZE - len_diff):
                                wave = np.append(wave, 0.0)
                            if self.fine.get(i) != 0:
                                    wave = self.pitch_shift(wave, np.power(2, self.fine.get(i)/100))
                            self.parent.wave_data.fix(wave, i)
                        else:
                            wave = vel.get(i)/127 * self.out_data.get(i)[self.parent.offset.get(i): self.parent.offset.get(i)+self._BUF_SIZE]
                            if self.fine.get(i) != 0:
                                    wave = self.pitch_shift(wave, np.power(2, self.fine.get(i)/100))
                            self.parent.wave_data.fix(wave, i)
                    elif self.parent.R_flag.get(i) == False:
                        if self.parent.offset.get(i) < start_pos:
                            wave = vel.get(i)/127 * self.out_data.get(i)[self.parent.offset.get(i): self.parent.offset.get(i)+self._BUF_SIZE]
                            if self.fine.get(i) != 0:
                                    wave = self.pitch_shift(wave, np.power(2, self.fine.get(i)/100))
                            self.parent.wave_data.fix(wave, i)
                            #print("通りました")
                        elif self.parent.offset.get(i) >= start_pos:
                            if self.parent.offset.get(i) < fade_pos:
                                wave = vel.get(i)/127 * self.out_data.get(i)[self.parent.offset.get(i): self.parent.offset.get(i)+self._BUF_SIZE]
                                if self.fine.get(i) != 0:
                                    wave = self.pitch_shift(wave, np.power(2, self.fine.get(i)/100))
                                self.parent.wave_data.fix(wave, i)
                            elif self.parent.offset.get(i) >= end_pos:
                                self.parent.pre_offset.fix(int(start_pos), i)
                                wave = vel.get(i)/127 * self.out_data.get(i)[int(start_pos): int(start_pos)+self._BUF_SIZE]
                                if self.fine.get(i) != 0:
                                    wave = self.pitch_shift(wave, np.power(2, self.fine.get(i)/100))
                                self.parent.wave_data.fix(wave, i)
                            elif self.parent.offset.get(i) >= fade_pos:
                                wave = (1.0 - (factor * (end_pos - self.parent.offset.get(i)))) * vel.get(i)/127 * self.out_data.get(i)[self.parent.offset.get(i): self.parent.offset.get(i)+self._BUF_SIZE]
                                wave = wave + factor * (end_pos - self.parent.offset.get(i)) * vel.get(i)/127 * self.out_data.get(i)[self.parent.offset.get(i): self.parent.offset.get(i)+self._BUF_SIZE]
                                if self.fine.get(i) != 0:
                                    wave = self.pitch_shift(wave, np.power(2, self.fine.get(i)/100))
                                self.parent.wave_data.fix(wave, i)
                


                
    def loopON(self, pos, length, fade):
        self.loop = True
        self.pos = pos
        self.length = length
        self.fade = fade
        
    def resampling(self, sig, pitchChangeRate, kind = "fourier"):
        sig = sig.tolist()
        L = len(sig)
        new_L = int(round(L / float(pitchChangeRate)))

        if kind == "fourier":
            new_sig = resample(sig, new_L)
        else:
            f = interp1d(arange(L), sig, kind = "linear")
            new_x = linspace(0, L - 1, num = new_L)
            new_sig = f(new_x)

        return np.array(new_sig, dtype=np.int16)
    
    def time_stretch(self, data, rate):
        rate = 1/rate
        W = 64
        fade_W = int(W/4)
        result = data[:W]
        for i in range(1, int(data.size/rate)):
            w0_start = int(rate * i * W)
            w0_fade = data[w0_start: w0_start+fade_W]
            w0 = data[w0_start+fade_W: w0_start+W]
            pre_fade = data[int(rate * (i-1) * W) + W: int(rate * (i-1) * W) + W + fade_W]

            coeff_pre = np.linspace(1, 0, fade_W)
            coeff_fade = np.linspace(0, 1, fade_W)
            if pre_fade.size == fade_W and w0_fade.size == fade_W:
                pre_fade = pre_fade * coeff_pre
                w0_fade = w0_fade * coeff_fade
                fade = pre_fade + w0_fade
                result = np.concatenate([result, fade, w0])
            else:
                pass
            
        return result
    
    def pitch_shift(self, data, rate):
        data_len = data.size
        #data = self.time_stretch(data, rate)
        data = self.resampling(data, rate)
        
        while data_len > data.size:
            data = np.append(data, data[-1])
            
        if data_len < data.size:
            data = data[:self._BUF_SIZE]
        
        return data
        
    def _upsampling(self, data, rate):
        """
        アップサンプリングを行う．
        入力として，変換レートとデータとサンプリング周波数．
        アップサンプリング後のデータとサンプリング周波数を返す．
        """
        # 補間するサンプル数を決める
        interpolationSampleNum = rate - 1
        
        data = data.tolist()

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
   
    
    def _downsampling(self, data, rate):
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
        data = scipy.signal.lfilter(b,1,data)
        data = data.tolist()
        #print(len(data))

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
        
        return np.array(data, dtype=np.int16)
    
    


# In[ ]:




