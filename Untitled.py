#!/usr/bin/env python
# coding: utf-8

# In[1]:


from synth import *
from interface import *
from sampler import Sampler
from amplifier import SimpleAmp
from controller import Envelope


# In[2]:


synth = Series(pitch=440, rate=16000, bufsize=50)


# In[3]:


synth.stack(MidiFromPCkey())


# In[4]:


sam = synth.stack(Sampler(wavefile="wizavo_outfile/men/wa-.wav"))
sam.loopON(pos=0.3, length=0.05, fade=0.7)
amp = synth.stack(SimpleAmp(volume=0.1))


# In[5]:


env = Envelope(A=0.1, D=0.1, S=1.0, R=0.1)
env.assign(amp.amp)
synth.implement(env)


# In[ ]:


synth.completed()
synth.play()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




