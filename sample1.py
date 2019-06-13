#!/usr/bin/env python
# coding: utf-8

# In[1]:


from synth import Series, Cabinet 
from interface import MidiFromPCkey
from oscillator import SineWave, TriangleWave, SquareWave
from amplifier import SimpleAmp
from controller import Envelope


# In[2]:


synth1 = Series(pitch=440, rate=44100, bufsize=500)


# In[3]:


if1 = synth1.stack(MidiFromPCkey())


# In[4]:


#synth1.stack(SquareWave())


# In[5]:


cab1 = synth1.stack(Cabinet([SquareWave(), TriangleWave()], ratio=[0.6, 0.4]))


# In[6]:


amp1 = synth1.stack(SimpleAmp())


# In[ ]:


env1 = Envelope(A=0.1, D=0.1, S=0.8, R=1.0)


# In[ ]:


env1.assign(amp1.amp)


# In[7]:


synth1.completed()
synth1.play()


# In[ ]:





# In[ ]:





# In[ ]:




