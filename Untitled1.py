#!/usr/bin/env python
# coding: utf-8

# In[1]:


import threading
import time
from note_seq.protobuf import music_pb2

from beatplayer import BeatPlayer

from synth import Series
from interface import SingNoteSequence
from oscillator import PulseWave
from FX import Lowpass
from amplifier import SimpleAmp
from controller import *


# In[2]:


def a():
    while True:
        print("hello")
        time.sleep(0.3)


# In[ ]:


bp = BeatPlayer("./beat/beat100.wav", 100, 8)

tb = Series()
tb_if = tb.stack(SingNoteSequence())
tb_osc = tb.stack(PulseWave(interval=24))
tb_lp = tb.stack(Lowpass(fs=1000, fp=10000))
tb_amp = tb.stack(SimpleAmp(volume=0.7))

tbe_amp = Envelope(A=0.01, D=0.2, S=0.6, R=0.2)
tbe_amp.assign(tb_amp.amp)

tb.implement(tbe_amp)
tb.completed()

twinkle_twinkle = music_pb2.NoteSequence()
# Add the notes to the sequence.
twinkle_twinkle.notes.add(pitch=60, start_time=0.0, end_time=0.5, velocity=80)
twinkle_twinkle.notes.add(pitch=60, start_time=0.5, end_time=1.0, velocity=80)
twinkle_twinkle.notes.add(pitch=67, start_time=1.0, end_time=1.5, velocity=80)
twinkle_twinkle.notes.add(pitch=67, start_time=1.5, end_time=2.0, velocity=80)
twinkle_twinkle.notes.add(pitch=69, start_time=2.0, end_time=2.5, velocity=80)
twinkle_twinkle.notes.add(pitch=69, start_time=2.5, end_time=3.0, velocity=80)
twinkle_twinkle.notes.add(pitch=67, start_time=3.0, end_time=4.0, velocity=80)
twinkle_twinkle.notes.add(pitch=65, start_time=4.0, end_time=4.5, velocity=80)
twinkle_twinkle.notes.add(pitch=65, start_time=4.5, end_time=5.0, velocity=80)
twinkle_twinkle.notes.add(pitch=64, start_time=5.0, end_time=5.5, velocity=80)
twinkle_twinkle.notes.add(pitch=64, start_time=5.5, end_time=6.0, velocity=80)
twinkle_twinkle.notes.add(pitch=62, start_time=6.0, end_time=6.5, velocity=80)
twinkle_twinkle.notes.add(pitch=62, start_time=6.5, end_time=7.0, velocity=80)
twinkle_twinkle.notes.add(pitch=60, start_time=7.0, end_time=8.0, velocity=80) 
twinkle_twinkle.total_time = 8
twinkle_twinkle.tempos.add(qpm=50);

print(twinkle_twinkle.tempos[0].qpm)

tb_if.set_note_sequence(twinkle_twinkle)
bp.play_beat()
#t1 = threading.Thread(target=bp.play_beat)
#t2 = threading.Thread(target=tb.play)
#t1.start()
#t2.start()
#tb.play()


# In[2]:


import time
import threading

class cl1():
    a = 0
    flag = True
    def func1(self):
        while self.flag:
            self.a = self.a + 1
            #print(a)
            time.sleep(0.2)

c = cl1()
th = threading.Thread(target=c.func1)
th.start()

while c.a < 20:
    #print("a: ", c.a)
    time.sleep(1.)

c.flag = False
th.join()
print("おわた")


# In[6]:


import serial
port = '/dev/cu.usbmodem141101'


# In[11]:


with serial.Serial(port, 9600,timeout=1) as ser:
    flag=bytes('0','utf-8')
    ser.write(flag)


# In[ ]:




