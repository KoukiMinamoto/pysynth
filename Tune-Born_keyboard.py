#!/usr/bin/env python
# coding: utf-8

# In[1]:


from synth import *
from interface import *
from sampler import Sampler
from oscillator import SineWave, TriangleWave, ToufuWave
from amplifier import SimpleAmp, WavWriter
from controller import Envelope, ArduinoController
from pitchdetection import MIDIDetection


# In[ ]:


pitch_log = []
syn = Series(bufsize=512, pitch=440, rate=44100)
interface = syn.stack(SingSong(pitch_log, chunk=512))
osc = syn.stack(ToufuWave())
amp = syn.stack(SimpleAmp(volume=0.8))

env = Envelope(A=0.04, D=0.05, S=0.6, R=0.1)
env.assign(amp.amp)
env2 = ArduinoController(com='/dev/cu.usbmodem141101', baudrate=9600)
env2.assign(osc.fine, scale=300.)

syn.implement(env)
syn.implement(env2)
syn.completed()
md = MIDIDetection()

while True:
    pitch_log, vel_log = md.mimic_song()
    interface.set_pitch_log(pitch_log)
    print(pitch_log)

    syn.play()


# In[ ]:




