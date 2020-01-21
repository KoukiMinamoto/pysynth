#!/usr/bin/env python
# coding: utf-8

# In[1]:


import serial
with serial.Serial('/dev/cu.usbmodem143101',9600,timeout=1) as ser:
    flag=bytes('180','utf-8')
    ser.write(flag)


# In[ ]:




