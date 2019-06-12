
# coding: utf-8

# In[1]:


import numpy as np


# In[2]:


get_ipython().magic('load_ext Cython')


# In[48]:


get_ipython().run_cell_magic('cython', '', 'cdef double py_fib(int n):\n    cdef double a = 0.0\n    cdef double b = 1.0\n    for i in range(n):\n        a, b = a + b, a\n    return a\n\ncdef void main():\n    py_fib(1)')


# In[49]:


get_ipython().magic('timeit main()')

