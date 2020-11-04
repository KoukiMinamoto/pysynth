#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pyaudio
import wave
import numpy as np
import sys


# In[3]:


class BeatPlayer(object):
    def __init__(self, beat_file, qpm, nquote, chunk=1024):
        self.beat_file = beat_file
        self.qpm = qpm
        self.chunk = chunk
        self.nquote = nquote
        self.state = -1
        self.vol = 1.0
        
        self.wf = wave.open(self.beat_file, "rb")
        self.p = pyaudio.PyAudio()
        self.frate = self.wf.getframerate()
        self.nframe = self.wf.getnframes()
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()), channels=self.wf.getnchannels(), rate=self.frate, output=True)
        
        self.quote_pos = [0]
        n = self.nframe / self.nquote
        for i in range(1, self.nquote):
            self.quote_pos.append(int(n*i))
        print("quote_pos:", self.quote_pos)
        print("frame_num", self.nframe)
        
    def play_beat(self, loop=True, fade=False):
        quote_frame = []
        
        quote = (self.nframe / self.chunk) / self.nquote
        print(quote)
        
        data = 0
        i = 0
        while data != b'':
            data = self.wf.readframes(self.chunk)
            arr_data = np.frombuffer(data, dtype='int16')
            if data == b'' and loop == True:
                i = 0
                self.wf = wave.open(self.beat_file, "rb")
                data = self.wf.readframes(self.chunk)
                arr_data = np.frombuffer(data, dtype='int16')
            arr_data = self.vol * arr_data
            self.stream.write(arr_data.astype(np.int16).tostring())
            
            minimum = i
            maximum = i + self.chunk
            for j, pos in enumerate(self.quote_pos):
                if pos >= minimum and pos < maximum:
                    self.state = (j % 4) + 1
                    print(self.state)
                else:
                    self.state = -1
        
            i = i + self.chunk
        
        self.close()
    
    def getState(self):
        return self.state
    
    def setVolume(self, vol):
        self.vol = vol
    
    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


# bp = BeatPlayer("./beat/beat100.wav", 100, 8)
# bp.play_beat()

# In[ ]:




