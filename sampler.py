#!/usr/bin/env python
# coding: utf-8

# In[3]:


import wave
import numpy
import pyaudio
import math
import scipy.signal


# In[56]:


class Sampler():
    
    def __init__(self, wavefile, bufsize=500, rate=44100):
        self.wavefile = wavefile
        self._BUF_SIZE = bufsize
        self._RATE = rate
        
        self.wr = wave.open(self.wavefile, "rb")
        self.data = self.wr.readframes(self.wr.getnframes())
        self.data = np.frombuffer(self.data, count=self.wr.getnframes(), offset=0, dtype=np.int16)
        
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self._RATE
                                      , frames_per_buffer=self._BUF_SIZE, output = True)
        
    
    def _standby(self):
        pass
    
    def _play(self, pitch):
        scale = pitch
        
        out = self.data
        
        if scale > 1.0:
            out = self._downsampling(out, scale)
        elif scale < 1.0:
            out = self._upsampling(out, 1/scale)
        
        out = self._fade_timestretch(out, scale=1.0/scale, fade_rate=0.8)
            
        output = self.stream.write(out.tostring())
        #self._write_file(out, file_name="./result/1oct_upper_f0.0.wav")
        
#         self.stream.stop_stream()
#         self.stream.close()
#         self.p.terminate()
#         self.wr.close()
        return out
    
    def _fade_timestretch(self, data, scale=1.0, fade_rate=0.4):
        div_sec = 0.05

        frame_num = len(data)
        div_frame = math.ceil(self._BUF_SIZE * div_sec)
        div_num = math.ceil(frame_num / div_frame)
        fade_frame = math.ceil(div_frame * fade_rate)

        print("frame_num: ", frame_num)
        print("div_frame: ", div_frame)
        print("div_num: ", div_num)

        out = []
        fade = [0] * fade_frame



        for i in range(int(div_num*(1/scale))): 
            offset = math.ceil(scale * div_frame * i)
            if i == 0:
                temp = data[offset: offset+div_frame]
                out.append(temp)
                temp = data[offset+div_frame: offset+div_frame+fade_frame]
                for j in range(fade_frame):
                    try:
                        fade[j] = fade[j] + math.ceil(temp[j] * (1.0 / fade_frame) * (fade_frame - j))
                    except IndexError:
                        pass
            else:
                temp = data[offset: offset+fade_frame]
                for j in range(fade_frame):
                    try:
                        fade[j] = fade[j] + math.ceil(temp[j] * (1.0 / fade_frame) * j)
                    except IndexError:
                        pass
                out.append(fade)
                fade = [0] * fade_frame
                temp = data[offset+fade_frame: offset+div_frame]
                out.append(temp)
                temp = data[offset+div_frame: offset+div_frame+fade_frame]
                for j in range(fade_frame):
                    try:
                        fade[j] = fade[j] + math.ceil(temp[j] * (1.0 / fade_frame) * (fade_frame - j))
                    except IndexError:
                        pass

        out = np.concatenate(out)
        numpy.set_printoptions(threshold=numpy.inf)
        out = np.array(out, dtype=np.int16)
        print(len(out))
        return out
    
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
        nyqF = self._RATE/2.0     # 変換後のナイキスト周波数
        cF = (self._RATE/2.0-500.)/nyqF             # カットオフ周波数を設定（変換前のナイキスト周波数より少し下を設定）
        taps = 511                          # フィルタ係数（奇数じゃないとだめ）
        b = scipy.signal.firwin(taps, cF)   # LPFを用意

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

        #間引き処理
        left = 0
        for i in range(len(data)):
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

    def _write_file(self, data, file_name):
        ww = wave.Wave_write(file_name)
        ww.setnchannels(1)
        ww.setsampwidth(2)
        ww.setframerate(self._RATE)
        ww.writeframes(data)
        ww.close()


# In[60]:


if __name__ == "__main__":
    sampler1 = Sampler(wavefile="./wizavo_outfile/men/a-.wav", bufsize=500, rate=16000)
    out = []
    sampler1._play(pitch=1.3)
#     for i in range(13):
#         if i == 1 or i == 3 or i == 6 or i == 8 or i == 10:
#             pass
#         else:
#             out.append(sampler1._play(pitch=np.power(2, i/12)).tolist())
#     out = np.concatenate(out)
#     sampler1._write_file(np.array(out, dtype=np.int16), "./result/ori-1oct_upper_ha-.wav")
    
#     out = []
#     for i in range(13):
#         if i == 2 or i == 4 or i == 6 or i == 9 or i == 11:
#             pass
#         else:
#             out.append(sampler1._play(pitch=np.power(2, -i/12)).tolist())
    
#     out = np.concatenate(out)
#     sampler1._write_file(np.array(out, dtype=np.int16), "./result/ori-1oct_downner_ha-.wav")
            


# In[ ]:





# In[ ]:




