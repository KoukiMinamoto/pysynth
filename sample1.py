#!/usr/bin/env python
# coding: utf-8

# In[1]:


from synth import Series, Cabinet 
from interface import MidiFromPCkey
from oscillator import SineWave, TriangleWave, SquareWave
from amplifier import SimpleAmp


# In[2]:


synth1 = Series(pitch=440, rate=44100, bufsize=500)


# In[3]:


synth1.stack(MidiFromPCkey())


# In[4]:


#synth1.stack(SquareWave())


# In[5]:


synth1.stack(Cabinet([SquareWave(), TriangleWave()], ratio=[0.6, 0.4]))


# In[6]:


synth1.stack(SimpleAmp())


# In[7]:


synth1.completed()
synth1.play()


# In[ ]:





# In[ ]:





# In[ ]:




