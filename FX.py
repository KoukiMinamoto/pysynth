#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import scipy 
from synth import *


# In[ ]:


class PitchShifter(object):
    
    def __init__(self, interval=0, fine=0):
        self.interval = 0
        self.fine = 0
    
    def stadby(self, synth):
        self.parent = synth
        self._BUF_SIZE = self.parent._BUF_SIZE
        self._RATE = self.parent._RATE
        self._PITCH = self.parent._PITCH
    
    def play(self):
        pass
    
    def 
        

