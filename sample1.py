#!/usr/bin/env python
# coding: utf-8

# In[1]:


from synth import Series, Cabinet 
from interface import MidiFromPCkey
from oscillator import SineWave, TriangleWave, SquareWave
from sampler import Sampler
from amplifier import SimpleAmp
from controller import Envelope


# In[2]:


synth1 = Series(pitch=440, rate=16000, bufsize=500)


# In[3]:


synth1.stack(MidiFromPCkey())


# In[4]:


osc = synth1.stack(TriangleWave())


# In[5]:


#synth1.stack(Cabinet([SquareWave(), TriangleWave()], ratio=[0.6, 0.4]))


# In[6]:


amp = synth1.stack(SimpleAmp(volume = 0.1))


# In[7]:


env = Envelope(A=1.3, D=0.5, S=0.8, R=1.0)


# In[8]:


env.assign(amp.amp)
env.assign(osc.interval, scale=1)


# In[9]:


synth1.implement(env)
#synth1.implement(env2)


# In[ ]:


synth1.completed()
synth1.play()


# In[ ]:




