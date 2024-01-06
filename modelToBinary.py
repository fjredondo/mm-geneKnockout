#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cplex
import cobra
import time
import pickle
import sys
cobra.Configuration().solver='cplex'


# In[2]:


start=time.time()

nombreEntrada=sys.argv[1]
nombreSalida=sys.argv[2]

ext=nombreEntrada[len(nombreEntrada)-3:]
if ext=="xml":
    modelo=cobra.io.read_sbml_model(nombreEntrada)
if ext=="mat":
    modelo=cobra.io.load_matlab_model(nombreEntrada)
    
with open(nombreSalida,"wb") as f:
    pickle.dump(modelo,f)

print(f'{"nombreSalida: "}{nombreSalida}{"; time: "}{(time.time()-start)}')

