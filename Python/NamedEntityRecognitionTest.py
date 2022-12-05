#!/usr/bin/env python
# coding: utf-8

# ## Import Dependencies

# In[6]:


import spacy
import os
import sys
from datetime import datetime
from elasticsearch import Elasticsearch


# ## Test Model

# In[10]:


dirpath = os.path.join("/", "Users", "vithya", "Programs", "Python")
#spacy.load(os.path.join(dirpath, "NamedEntityRecognitionModel"))
nlp = spacy.load(os.path.join(dirpath, "NamedEntityRecognition"))
f = open(sys.argv[1])
doc = nlp(f.read().replace("\n", "").replace("\xa0"," "))
for ent in doc.ents:
    print(ent.start_char, ent.end_char, ent.text, ent.label_)


# ## Elastic Search

# In[11]:
'''

es = Elasticsearch("https://localhost:9200",
                   ca_certs=False,
                   verify_certs=False,
                   http_auth=('elastic', '*XxotzsQktEZZ+9fGZi-'))


# In[13]:


#Adding Names
for ent in doc.ents:
    query = {
        ent.label_ : ent.text
    }
    es.index(index='index11', document=query) 
'''

# In[ ]:




