#!/usr/bin/env python
# coding: utf-8

# In[1]:


from synth import Series
from interface import MidiFromPCkey
from sampler import Sampler
from amplifier import SimpleAmp
from controller import Envelope


# In[ ]:


synth = Series(pitch=440, rate=16000, bufsize=500)
synth.stack(MidiFromPCkey())
sampler = synth.stack(Sampler(wavefile="./wizavo_outfile/men/wa-.wav"))
amp = synth.stack(SimpleAmp(volume=0.1))
env = Envelope(A=0.1, D=0.05, S=1.0, R=0.1)
env.assign(amp.amp)
synth.implement(env)
synth.completed()
synth.play()


# In[ ]:





# In[ ]:





# In[ ]:




