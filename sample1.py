#!/usr/bin/env python
# coding: utf-8

# In[1]:


from synth import Series, Cabinet 
from interface import MidiFromPCkey
from oscillator import SineWave, TriangleWave, SquareWave, WizavoPCM
from amplifier import SimpleAmp


# In[2]:


synth1 = Series(pitch=440, rate=16000, bufsize=500)


# In[3]:


synth1.stack(MidiFromPCkey())


# In[4]:


synth1.stack(WizavoPCM())


# In[5]:


#synth1.stack(Cabinet([SquareWave(), TriangleWave()], ratio=[0.6, 0.4]))


# In[6]:


synth1.stack(SimpleAmp())


# In[ ]:


synth1.completed()
synth1.play()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




