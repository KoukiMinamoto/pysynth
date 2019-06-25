#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from pysynth.synth import Series
from pysynth.interface import MidiFromPCkey
from pysynth.sampler import Sampler
from pysynth.amplifier import SimpleAmp
from pysynth.controller import Envelope

synth = Series(pitch=440, rate=16000, bufsize=500)
synth.stack(MidiFromPCkey())

# Set wavefile you want to sample.
sampler = synth.stack(Sampler(wavefile="../wizavo_outfile/men/wa-.wav"))
amp = synth.stack(SimpleAmp(volume=0.1))

env = Envelope(A=0.1, D=0.05, S=1.0, R=0.1)
env.assign(amp.amp)
synth.implement(env)

synth.completed()
synth.play()

