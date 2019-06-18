#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import scipy.signal
import wave


# In[2]:


class SineWave():
    """ * サイン波を生成するモジュール *
        arg: 周波数, オフセット
        return: 波形データ配列(np.arry)
    """
    def __init__(self):
        self.name = "SineWave"
        self.val = None
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500

    def _standby(self, pitch=440, rate=44100, bufsize=500):
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        
        return [self.name]
    
    def _play(self, freq, offsets, amp, length):
        out = self._sine(freq, offsets, amp, length)
        
        return out
    
    def _sine(self, freq, offsets, amp, length):
        out = np.zeros(length, dtype=np.float32)
        length = int(length)
        
        if len(freq) > 0:
            for i in range(len(freq)):
                factor = float(freq[i]) * (np.pi*2)/self._RATE
                wave = []
                wave.append(np.sin(np.arange(offsets[i], offsets[i]+length) * factor))
                wave = np.concatenate(wave) * amp
                out = out + wave
        else:
            pass
        
        return out

class TriangleWave():
    """ * サイン波を生成するモジュール *
        arg: 周波数, オフセット
        return: 波形データ配列(np.arry)
    """
    def __init__(self):
        self.name = "SineWave"
        self.val = None
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500

    def _standby(self, pitch=440, rate=44100, bufsize=500):
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        
        return [self.name]
    
    def _play(self, freq, offsets, amp, length):
        out = self._sine(freq, offsets, amp, length)
        
        return out
    
    def _sine(self, freq, offsets, amp, length):
        out = np.zeros(length, dtype=np.float32)
        length = int(length)
        
        if len(freq) > 0:
            for i in range(len(freq)):
                factor = float(freq[i]) * (np.pi*2)/self._RATE
                wave = []
                wave.append(scipy.signal.sawtooth(np.arange(offsets[i], offsets[i]+length) * factor))
                wave = np.concatenate(wave) * amp
                out = out + wave
        else:
            pass
        
        return out


# In[3]:


class SquareWave():
    """ * サイン波を生成するモジュール *
        arg: 周波数, オフセット
        return: 波形データ配列(np.arry)
    """
    def __init__(self):
        self.name = "SquareWave"
        self.val = None
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500

    def _standby(self, pitch=440, rate=44100, bufsize=500):
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        
        return [self.name]
    
    def _play(self, freq, offsets, amp, length):
        out = self._sine(freq, offsets, amp, length)
        
        return out
    
    def _sine(self, freq, offsets, amp, length):
        out = np.zeros(length, dtype=np.float32)
        length = int(length)
        
        if len(freq) > 0:
            for i in range(len(freq)):
                factor = float(freq[i]) * (np.pi*2)/self._RATE
                wave = []
                wave.append(scipy.signal.square(np.arange(offsets[i], offsets[i]+length) * factor))
                wave = np.concatenate(wave) * amp
                out = out + wave
        else:
            pass
        
        return out


# In[1]:


class WizavoPCM():
    """ * サイン波を生成するモジュール *
        arg: 周波数, オフセット
        return: 波形データ配列(np.arry)
    """
    def __init__(self):
        self.name = "WizavoPCM"
        self.val = None
        
        self._PITCH = 440
        self._RATE = 44100
        self._BUF_SIZE = 500
        self.wavfile = "./wizavo_outfile/men/a-.wav"
        # WAVファイルを開く
        self.wr = wave.open(self.wavfile, "rb")
        self.data = self.wr.readframes(self.wr.getnframes())

    def _standby(self, pitch=440, rate=44100, bufsize=500):
        self._PITCH = pitch
        self._RATE = rate
        self._BUF_SIZE = bufsize
        
        return [self.name]
    
    def _play(self, freq, offsets, amp, length):
        out = self._sing(freq, offsets, amp, length)
        
        return out
    
    def _sing(self, freq, offsets, amp, length):
        num_data = np.zeros(length, dtype=np.float32)
        
        if len(freq) > 0:
            print("offsets: ", offsets[0])
            if offsets[0] >= self.wr.getnframes():
                pass
            else:
                num_data = np.frombuffer(self.data, count=self._BUF_SIZE, offset=offsets[0], dtype = np.int16)
        
        return num_data


# In[ ]:




