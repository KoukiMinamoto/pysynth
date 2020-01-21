#!/usr/bin/env python
# coding: utf-8

# In[1]:


from synth import Series
from interface import MonoMeledy, SingSong
from oscillator import SineWave, TriangleWave
from amplifier import SimpleAmp
from controller import Envelope
from pitchdetection import PitchDetection


# In[3]:


pd = PitchDetection()
pitch_log = pd.mimic_song()
print(pitch_log)

syn = Series(bufsize=512, pitch=440, rate=44100)
interface = syn.stack(SingSong(pitch_log, chunk=2048))
osc = syn.stack(SineWave())
amp = syn.stack(SimpleAmp(volume=1.0))

env = Envelope(A=0.1, D=0.1, S=1.0, R=0.1)
env.assign(amp.amp)
syn.implement(env)

syn.completed()
syn.play()


# In[ ]:


pitch_log = []
syn = Series(bufsize=512, pitch=440, rate=44100)
interface = syn.stack(SingSong(pitch_log, chunk=2048))
osc = syn.stack(SineWave())
amp = syn.stack(SimpleAmp(volume=1.0))

env = Envelope(A=0.1, D=0.1, S=1.0, R=0.1)
env.assign(amp.amp)
syn.implement(env)
syn.completed()

while True:
    pd = PitchDetection()
    pitch_log = pd.mimic_song()
    interface.set_pitch_log(pitch_log)
    print(pitch_log)

    syn.play()


# In[ ]:




