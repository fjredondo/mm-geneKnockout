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
with open(nombreEntrada,"rb") as f:
    modelo=pickle.load(f)


# In[29]:


print(f'{"filename: "}{f.name}')


# In[3]:


susGenes=dict()
for r in modelo.reactions:
    grr=r.gene_reaction_rule
    if len(r.genes)==0:
        susGenes[r.id]=set()
    if len(r.genes)==1:
        susGenes[r.id]=set([g.id for g in r.genes])
    if "or" in grr and not "and" in grr:
        susGenes[r.id]=set()
    if "and" in grr and not "or" in grr:
        susGenes[r.id]= set(grr.split(" and "))
    if "and" in grr and "or" in grr:
        susGenes[r.id]=set([g.id for g in r.genes])


# In[5]:


biomasa=modelo.reactions.MAR13082
error=10**-12
with modelo:
    modelo.objective=biomasa
    modelo.objective_direction="max"
    sol=modelo.optimize()
    sop=[r.id for i,r in enumerate(modelo.reactions) if abs(sol.fluxes[i])>error]


# In[30]:


print(f'{"biomasa.id: "}{biomasa.id}')


# In[32]:


print(f'{"len(sop): "}{len(sop)}')


# In[34]:


candidatos=set()
for r in sop:
    candidatos.update(susGenes[r])


# In[36]:


print(f'{"len(candidatos): "}{len(candidatos)}{"; len(modelo.genes): "}{len(modelo.genes)}')


# In[ ]:


gCS=set()
for g in candidatos:
    with modelo:
        modelo.genes.get_by_id(g).knock_out()
        biomasa.bounds=[error,1000]
        modelo.objective=biomasa
        modelo.objective_direction="max"
        sol=modelo.slim_optimize()
        if sol<error:
            gCS.add(g)


# In[ ]:


print(f'{"len(gCS): "}{len(gCS)}')


# In[21]:


with open(nombreSalida,"wb") as f:
    pickle.dump(gCS,f)


# In[38]:


print(f'{"nombreSalida: "}{nombreSalida}{"; time: "}{(time.time()-start)}')

