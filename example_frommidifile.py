#!/usr/bin/env python
# coding: utf-8

# In[1]:


from synth import Series
from interface import FromMidiFile
from sampler import Sampler
from oscillator import SineWave, TriangleWave
from amplifier import SimpleAmp
from controller import Envelope


# In[ ]:


# Construction
synth = Series(pitch=440, rate=44100, bufsize=500)
interface = synth.stack(FromMidiFile(midifile="./midi_file/Super Mario 64 - Medley.mid"))
#sampler = synth.stack(Sampler(wavefile="./wizavo_outfile/men/wa-.wav"))
osc = synth.stack(TriangleWave())
amp = synth.stack(SimpleAmp(volume=0.1))

# Envelopes
env = Envelope(A=0.1, D=0.2, S=1.0, R=0.3)
env.assign(amp.amp)
synth.implement(env)

# Switches
#sampler.loopON(pos=0.3, length=0.05, fade=0.6)

# run
synth.completed()
synth.play()

