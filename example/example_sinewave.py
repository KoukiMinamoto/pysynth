#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from pysynth.synth import Series
from pysynth.interface import MidiFromPCkey
from pysynth.oscillator import SineWave, TriangleWave, SquareWave
from pysynth.amplifier import SimpleAmp
from pysynth.controller import Envelope

# Instance your synth.
synth = Series(pitch=440, rate=16000, bufsize=500)

# First, stack interface module.
in_layer = synth.stack(MidiFromPCkey())

# Second, stack  oscillator module.
osc_sine = synth1.stack(SineWave())
#osc_sine = synth1.stack(TriangleWave())
#osc_sine = synth1.stack(SquareWave())

# At last layer, stack amplifier module. 
amp_simple = synth1.stack(SimpleAmp(volume = 0.1))

# Make Envelope with ADSR.
env = Envelope(A=1.3, D=0.5, S=0.8, R=1.0)
# Assign paramter to envelope.
env.assign(amp.amp)
# Implement envelope to your synth.
synth.implement(env)

# Finally, run these method below.
synth.completed()
synth.play()


# In[ ]:




