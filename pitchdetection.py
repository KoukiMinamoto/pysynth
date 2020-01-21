#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pyaudio
import numpy as np
from scipy import signal
from scipy import interpolate
import matplotlib.pyplot as plt
import serial
import pygame
import pygame.midi
from time import sleep


# In[ ]:


class MIDIDetection(object):
    def __init__(self, rate=44100, bufsize=512, pitch=440):
        self.RATE = rate
        self.BUFSIZE = bufsize
        self.PITCH = pitch
        self.sleep_time = self.BUFSIZE/self.RATE
        self.silent_thresh = 1.0
        
        pygame.init()
        pygame.midi.init()
        input_id = pygame.midi.get_default_input_id()
        self.midi_in = pygame.midi.Input(input_id, self.BUFSIZE)
        
    def _getMIDI(self):
        note_num = -1
        vel = -1
        timestamp = -1
        note_on = -1
        if self.midi_in.poll():
            midi_events = self.midi_in.read(self.BUFSIZE)
            for event in midi_events:
                print(event)
                note_num = event[0][1]
                note_on = event[0][0]
                vel = event[0][2]
                timestamp = event[1]
                
        return note_num, note_on, vel, timestamp
    
    def mimic_song(self):
        pitch_list = []
        vel_list = []
        time_list = []
        note_on = 128
        start_flag = False
        end_flag = False
        silent_time = 0
        print("Listening your play...")
        while end_flag == False:
            #print(pitch_list)
            note_num, note_on, vel, timestamp = self._getMIDI()
            if note_on == 144:
                start_flag = True
                silent_time = 0
                pitch_list.append(note_num)
                vel_list.append(vel)
            elif note_on == 128:
                #pitch_list.append(0)
                vel_list.append(vel)
                silent_time = 0
            else:
                # 無音の時間が閾値を超えたら入力終了フラグを立ててwhileを抜ける    
                silent_time = silent_time + self.sleep_time
                if silent_time > self.silent_thresh and start_flag == True:
                    print("Input ends")
                    break
                elif start_flag == True:
                    pitch_list.append(pitch_list[-1])
            sleep(self.sleep_time)
                
        return pitch_list, vel_list
                


# In[ ]:


class PitchDetection(object):
    def __init__(self, rate=44100, bufsize=2048, pitch=440):
        self.RATE = rate
        self.BUFSIZE = bufsize
        self.PITCH = pitch
        self.W = self.BUFSIZE+self.BUFSIZE//2
        self.input = np.zeros(self.BUFSIZE+self.BUFSIZE//2)
        self.x_axis=np.fft.fftfreq(self.input.size, d=1.0/self.RATE)
        self.alpha = 0.9
        self.detected_freq = 0.0
        self.detected_pitch = 0.0
        # mimic_songで使う
        # 音声入力レベルの閾値
        self.threshold = 0.05
        # 歌い終わったと判断する無音時間
        self.silent_thresh = 1.0
        self.silent_thresh = self.silent_thresh * rate
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.RATE, frames_per_buffer=self.BUFSIZE, input=True, output=True)
        self.stream.stop_stream()
    
    def _get_signal(self):
        if self.stream.is_active():
            input = self.stream.read(self.BUFSIZE)
            buf = np.frombuffer(input, count=self.BUFSIZE, offset=0, dtype=np.int16) / 32768.0
        else:
            input = null
        
        return buf
    
    def _calc_m(self):
        m = np.zeros(self.BUFSIZE+self.BUFSIZE//2)
        m0 = np.power(self.input, 2)
        m0 = 2 * np.sum(m0)
        m[0] = m0
        for i in range(1, self.BUFSIZE+self.BUFSIZE//2):
            m[i] = m[i-1] - self.input[i-1] - self.input[-i]
        
        return m
        
    def mimic_song(self):
        pitch_log = []
        start_flag = False
        end_flag = False
        silent_time = 0
        self.stream.start_stream()
        print("Listening your singing...")
        while end_flag == False:
            # ピッチ検出
            # ①音声をマイクから読み込む
            raw_input = self._get_signal()
            max_level = max(raw_input)
            #print(max_level)
            if max_level > self.threshold:
                start_flag = True
                silent_time = 0
                # ② w=BUFSIZE/2 のサイズのゼロパディングをする
                zp = np.zeros(self.BUFSIZE//2)
                self.input = np.concatenate([raw_input, zp])
                # ③ パワースペクトルを求める
                F = np.fft.fft(self.input)
                ps = np.power(np.abs(F), 2)
                # ④ 逆フーリエする
                r = np.fft.ifft(ps).real
                # ⑤ NSDFを求める
                m = self._calc_m()
                n = np.zeros(self.BUFSIZE+self.BUFSIZE//2)
                for j in range(self.BUFSIZE+self.BUFSIZE//2):
                    n[j] = 2 * r[j] / m[j]
                n = n[:self.W//2]
                n[0] = 0.0
                # ⑥ 極大値を取得
                maxId = signal.argrelmax(n)
                maxId = maxId[0][1:]
                maxval = []
                for id in maxId:
                    maxval.append(n[id])
                # ⑦ 二次補間する
                newx = np.arange(0, maxId[-1])
                interp = interpolate.spline(maxId, maxval, xnew=newx)
                # ⑧ 周波数とピッチを求める
                peakId = signal.argrelmax(interp)
                peakId = peakId[0]
                threshold = self.alpha * np.max(interp)
                for id in peakId:
                    if interp[id] > threshold:
                        self.detected_freq = self.RATE / id
                self.detected_pitch = np.log10(self.detected_freq/8.2)/np.log10(np.power(2,1/12))
                if self.detected_pitch > 100.0:
                    self.detected_pitch = self.detected_pitch / 2.0
                pitch_log.append(round(self.detected_pitch))
            else:
                # 無音の時間が閾値を超えたら入力終了フラグを立ててwhileを抜ける    
                silent_time = silent_time + self.BUFSIZE
                if silent_time > self.silent_thresh and start_flag == True:
                    end_flag = True
                    self.stream.stop_stream()
                elif start_flag == True:
                    pitch_log.append(0)
        return pitch_log
            
        
        
    def run(self):
        self.stream.start_stream()
        for i in range(100):
            # ① 音声をマイクから読み込む
            raw_input = self._get_signal()
            # ② w=BUFSIZE/2 のサイズのゼロパディングをする
            zp = np.zeros(self.BUFSIZE//2)
            self.input = np.concatenate([raw_input, zp])
            # ③ パワースペクトルを求める
            F = np.fft.fft(self.input)
            ps = np.power(np.abs(F), 2)
            # ④ 逆フーリエする
            r = np.fft.ifft(ps).real
            # ⑤ NSDFを求める
            m = self._calc_m()
            n = np.zeros(self.BUFSIZE+self.BUFSIZE//2)
            for j in range(self.BUFSIZE+self.BUFSIZE//2):
                n[j] = 2 * r[j] / m[j]
            n = n[:self.W//2]
            n[0] = 0.0
            # ⑥ 極大値を取得
            maxId = signal.argrelmax(n)
            maxId = maxId[0][1:]
            maxval = []
            for id in maxId:
                maxval.append(n[id])
            if i > 10:
                # ⑦ 二次補間する
                newx = np.arange(0, maxId[-1])
                interp = interpolate.spline(maxId, maxval, xnew=newx)
                # ⑧ 周波数とピッチを求める
                peakId = signal.argrelmax(interp)
                peakId = peakId[0]
                threshold = self.alpha * np.max(interp)
                for id in peakId:
                    if interp[id] > threshold:
                        self.detected_freq = self.RATE / id
                self.detected_pitch = np.log10(self.detected_freq/8.2)/np.log10(np.power(2,1/12))
            
            # 結果表示用   
            if i == 50:
                print("周波数: ", self.detected_freq)
                print("ノートナンバー: ", self.detected_pitch)
                octave = self.detected_pitch // 12
                pitch = round(self.detected_pitch % 12)
                if pitch == 0:
                    print("音階: C", octave)
                elif pitch == 1:
                    print("音階: C#", octave)
                elif pitch == 2:
                    print("音階: D", octave)
                elif pitch == 3:
                    print("音階: D#", octave)
                elif pitch == 4:
                    print("音階: E", octave)
                elif pitch == 5:
                    print("音階: F", octave)
                elif pitch == 6:
                    print("音階: F#", octave)
                elif pitch == 7:
                    print("音階: G", octave)
                elif pitch == 8:
                    print("音階: G#", octave)
                elif pitch == 9:
                    print("音階: A", octave)
                elif pitch == 10:
                    print("音階: A#", octave)
                elif pitch == 11:
                    print("音階: B", octave)
                return self.detected_pitch
#                 fig, (axL, axC, axR) = plt.subplots(ncols=3, figsize=(15,4), sharex=True)
#                 axL.plot(np.arange(0,r.size), r, linewidth=2)
#                 axL.set_title('autocorretion')
#                 axL.set_xlim(0, 768)
#                 axL.grid(True)
#                 axC.plot(np.arange(0,n.size), n, linewidth=2)
#                 axC.set_title('NSDF')
#                 axC.grid(True)
#                 axR.plot(np.arange(0,interp.size), interp, linewidth=2)
#                 axR.set_title('Interpolation')
#                 axR.grid(True)
#                 fig.show()


# In[ ]:


# if __name__ == "__main__":
    
#     pd = PicthDetection()
#     pd.run()


# In[ ]:




