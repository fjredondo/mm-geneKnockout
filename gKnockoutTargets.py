#!/usr/bin/env python
# coding: utf-8

# In[4]:


import cplex
import cobra
import time
import pickle
cobra.Configuration().solver='cplex'


# In[82]:


## ---------------------------------------------------
## load_pickle: loads data stored by pickle into files into memory.
## Params: Receive a path
## Return: An object of type "set" or type "cobra.core.model.Model", depending the file content.
## ---------------------------------------------------
def load_pickle(ruta):
    with open(ruta,"rb") as f:
        cs=pickle.load(f)
        if isinstance(cs, set):
            print(f'{"len("}{ruta}{"): "}{len(cs)}')
        if isinstance(cs, cobra.core.model.Model):
            print(f'{"Loaded model: "}{ruta}')            
    return cs

from pathlib import Path

## ---------------------------------------------------
## load_files: invoke load_file for each file matching 
## the extension and path indicated in the parameters
## Params: Receive a file extension and path
## Return: A dictionary.
## ---------------------------------------------------
def load_files(ext,path):
    d=dict()
    for r in [ archivo.with_suffix("." + ext).as_posix()                  for archivo in Path(path).glob("*")]: 
        d[Path(r).stem] = load_pickle(r)
    return d

## ---------------------------------------------------
## recursive_operation_over_sets: Recursively applies the indicated operation
## on the set of elements passed in the dictionary
## Params: Receive a dictionary and the operation
## Return: A dictionary.
## ---------------------------------------------------
def recursive_operation_over_sets(d,o):
    k=list(d)
    s=list(d.values())
    newDict = dict()
    if len(s) > 1:
        # print(f'{[{i[0]:len(i[1])} for i in d.items()]}')
        t=eval("s[0]."+ o +"(s[1])")
        print(f'{"Operation: "}{[k[0],len(s[0])]}{" "}{o}{" "}{[k[1],len(s[1])]}{". Result: "}{len(t)}')
        s.pop(0)
        s.pop(0)
        s.insert(0,t)
        
        k.pop(0)
        k.pop(0)
        k.insert(0,o+'Target')        
        
        newDict = {k[i]: s[i] for i in range(len(k))}
        d=recursive_operation_over_sets(newDict,o)
    return d

## ---------------------------------------------------
## cal_knockout: Knockout a gene and calculate the biomass after optimizing the model
## Params: Receive a gene and model
## Return: A biomass calculation
## ---------------------------------------------------
def cal_knockout(g,model):
    with model:
        sol=-1
        if model.genes.has_id(g):
            model.genes.get_by_id(g).knock_out()
            sol= model.slim_optimize()
    return round(sol,4)


# In[8]:


generic_gcs_dict=load_files("gcs","./models/generic/gcs")
mm_gcs_dict=load_files("gcs","./models/mm/gcs")
tissue_gcs_dict=load_files("gcs","./models/tissue/gcs")


# In[54]:


mm_gcs = recursive_operation_over_sets(mm_gcs_dict.copy(), 'intersection')


# In[58]:


mm_gcs_without_generics = {**mm_gcs,**generic_gcs_dict}
mm_gcs_without_generics = recursive_operation_over_sets(mm_gcs_without_generics,'difference')


# In[59]:


mm_gcs_without_gTissue = {**mm_gcs_without_generics,**tissue_gcs_dict}
mm_gcs_without_gTissue = recursive_operation_over_sets(mm_gcs_without_gTissue,'difference')


# In[60]:


mm_gcs_without_gTissue


# In[ ]:


generic_data_dict=load_files("dat","./models/generic/data")
mm_data_dict=load_files("dat","./models/mm/data")
tissue_data_dict=load_files("dat","./models/tissue/data")


# In[109]:


biomassAfterGeneKnockout=[['Gene']+list(mm_data_dict)+list(generic_data_dict)+list(tissue_data_dict)]
for g in list(mm_gcs_without_gTissue.values())[0]:
    sol=[g]
    for m in list(mm_data_dict.values()):
        sol.append(cal_knockout(g, m))    
    for m in list(generic_data_dict.values()):
        sol.append(cal_knockout(g, m))         
    for m in list(tissue_data_dict.values()):
        sol.append(cal_knockout(g, m))
    biomassAfterGeneKnockout.append(sol)
print(biomassAfterGeneKnockout)   


# In[110]:


import numpy as np

np.savetxt("biomassAfterGeneKnockout.csv", biomassAfterGeneKnockout, delimiter=",", fmt="% s")

