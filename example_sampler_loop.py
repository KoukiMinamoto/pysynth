#!/usr/bin/env python
# coding: utf-8

# In[7]:


from synth import *
from interface import *
from sampler import Sampler
from amplifier import SimpleAmp, WavWriter
from controller import Envelope


# In[8]:


synth = Series(pitch=440, rate=16000, bufsize=50)


# In[9]:


synth.stack(MidiFromPCkey())


# In[10]:


sam = synth.stack(Sampler(wavefile="wizavo_outfile/men/wa-.wav"))
sam.loopON(pos=0.3, length=0.05, fade=0.6)
#amp = synth.stack(WavWriter(volume=0.1, file_name="result/melo_ha-.wav"))
amp = synth.stack(SimpleAmp(volume=0.1))


# In[11]:


env = Envelope(A=0.1, D=0.1, S=1.0, R=0.1)
env.assign(amp.amp)
synth.implement(env)


# In[12]:


synth.completed()
synth.play()

