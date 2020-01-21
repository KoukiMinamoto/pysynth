#!/usr/bin/env python
# coding: utf-8

# In[1]:


from synth import Series
from interface import MidiFromPCkey
from oscillator import SineWave, TriangleWave, ToufuWave
from amplifier import SimpleAmp
from controller import Envelope
from pitchdetection import PitchDetection
from controller import Envelope, ArduinoController


# In[ ]:


syn = Series(bufsize=512, pitch=440, rate=44100)
interface = syn.stack(MidiFromPCkey())
osc = syn.stack(SineWave())
amp = syn.stack(SimpleAmp(volume=1.0))

env = Envelope(A=0.1, D=0.1, S=1.0, R=0.1)
env.assign(amp.amp)

syn.implement(env)
syn.completed()
syn.play()


# In[ ]:




