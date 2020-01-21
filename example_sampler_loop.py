#!/usr/bin/env python
# coding: utf-8

# In[1]:


from synth import *
from interface import *
from sampler import Sampler
from oscillator import SineWave, TriangleWave, ToufuWave
from amplifier import SimpleAmp, WavWriter
from controller import Envelope, ArduinoController


# In[2]:


synth = Series(pitch=440, rate=44100, bufsize=512)


# In[3]:


synth.stack(MIDIkeyboard())
#synth.stack(MonoMeledy(72, 3.0))


# In[ ]:


#sam = synth.stack(Sampler(wavefile="wizavo_outfile/men/wa-_edited.wav"))
osc = synth.stack(ToufuWave(interval=12))
#sam.loopON(pos=0.5, length=0.1, fade=0.9)
#amp = synth.stack(WavWriter(volume=0.1, file_name="result/melo_ha-.wav"))
amp = synth.stack(SimpleAmp(volume=0.5))


# In[ ]:


env = Envelope(A=0.01, D=0.03, S=0.5, R=0.2)
#env3 = Envelope(A=0.05, D=0.3, S=0.0, R=0.2)
#env3.assign(osc.fine, scale=100.)
#env2 = ArduinoController(com='/dev/cu.usbmodem14301', baudrate=9600)
#env2.assign(osc.fine, scale=100.)
env.assign(amp.amp)
synth.implement(env)
#synth.implement(env2)
#synth.implement(env3)


# In[ ]:


synth.completed()
synth.play()


# In[ ]:





# In[ ]:




