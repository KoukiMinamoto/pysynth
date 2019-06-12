#!/usr/bin/env python
# coding: utf-8

# # こんな感じにしたい案１

# In[4]:


from synth import Synth
from interface import MidiFromPCkey 
from oscillator import SineWave
from amplifier import SimpleAmp
from fx import Filter
from modulation import Envelope, LFO, Control
from output.output import Output as output


# In[2]:


synth = Synth()


# In[ ]:


if1 = synth.add(MidiFromPCkey())


# In[ ]:


osc1 = synth.add(SineWave())


# In[ ]:


osc1 = synth.add(osc.sinewave())


# In[ ]:


fil = synth.add(Filter.prametric())


# In[ ]:


synth.add(output.from_pc())


# In[ ]:


env1 = Envelope(A=0.5, D=0.2, S=2.0, R=0.5)
env1.assign(osc1, osc1.amp, init=0.5, rang=0.2)


# In[ ]:


ctrl1 = Control()
ctrl1.assign(fil, fil.frequency, init=200, rang=1000)


# In[ ]:


synth.add_control(env1, ctrl1)


# In[ ]:


# PCキーボードで簡易的にプレイ
synth.play_onPC()

