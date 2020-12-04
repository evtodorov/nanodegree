#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"></ul></div>

# In[1]:


from pprint import pprint
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client.osm_data
sbg = db.SouthBG


# In[2]:


##Display statistics about the database
# mongoschema is available via pip, see also https://github.com/nimeshkverma/mongo_schema/
# some modification were required to make mongoschema compatible with Python 3.6
from mongoschema.mongoschema import Schema
schema = Schema("osm_data", "SouthBG")
num_docs, result = schema.get_schema()
schema.print_schema()


# In[3]:


# Set convenience constants
EXISTS = {"$exists": True}
NOT_NULL = lambda x: {"$ifNull": [ x, 0 ]}
NOT_NULL("test")


# In[4]:


# Count unique useres
len(sbg.distinct("created.uid"))


# In[5]:


# Count different classes of documents
pipeline = [{"$group": { "_id": "$class",
                        "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}]
list(sbg.aggregate(pipeline))


# In[6]:


sbg.count_documents({"power": EXISTS})


# In[7]:


## Question 3.1 - Explore types fields related to power
pipeline = [{"$match": {"power": EXISTS}},
            {"$group": { "_id": "$power",
                        "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}]
list(sbg.aggregate(pipeline))


# In[8]:


## Question 3.1 - Count source of the power when plant or generator
pipeline = [{"$match": {"$or":[ {"power": 'generator'},
                                {"power": 'plant'}]}},
            {"$project":  {"power": 1,
                           "source": {"$ifNull": ["$generator.source",
                                                "$plant.source"]}}},
            {"$group": { "_id": "$source",
                        "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}]
list(sbg.aggregate(pipeline))


# In[9]:


## Question 3.1 - Explore if it is possible to calculate the total output of each source
pipeline = [{"$match": {"$or":[ {"power": 'generator'},
                                {"power": 'plant'}]}},
            {"$project":  {"power": 1,
                           "name": 1,
                           "source": {"$ifNull": ["$generator.source",
                                                "$plant.source"]},
                          "output": {"$ifNull": ["$generator.output.electricity",
                                                "$plant.output.electricity"]}}}]
list(sbg.aggregate(pipeline))


# In[10]:


##Question 3.2 Count the different entities which have a website
# different types of objects (with different schemas) can have a website
pipeline = [{"$match": {"class": "node",
                        "website": EXISTS}},
            {"$project": {"entity": {"$switch": {"branches": [  {"case": NOT_NULL("$amenity"),
                                                                 "then": "$amenity"},
                                                                {"case": NOT_NULL("$shop"),
                                                                 "then": {"$concat": [{"$cond": [{"$eq": ["$shop",
                                                                                                          'yes']},
                                                                                                 "",
                                                                                                 "$shop"]},
                                                                                      " ",
                                                                                      "shop"]}},
                                                                {"case": NOT_NULL("$place"),
                                                                 "then": "$place"},
                                                                {"case": NOT_NULL("$tourism"),
                                                                 "then": "$tourism"},
                                                                {"case": NOT_NULL("$office"),
                                                                 "then": "office"}],
                                                 "default": None}}}},
            {"$group": { "_id": "$entity",
                        "count": {"$sum": 1}}},
            {"$match": {"count": {"$gte": 5}}},
            {"$sort": {"count": -1}}]
list(sbg.aggregate(pipeline))


# In[11]:


#Q3.2 further exploration - how many of the restaurants have website
pipeline = [{"$match": {"amenity": "restaurant"}},
            {"$project": { "has_website": {"$convert": {"input": "$website",
                                                        "to": "bool" }}}},
            {"$group": {"_id": "$has_website",
                        "count": {"$sum": 1}}},
            {"$project": {"has_website": "$_id", "count": 1, "_id": 0}}]
list(sbg.aggregate(pipeline))


# In[12]:


#Q3.2 further exploration - what other entities have websites
list(sbg.find({"website": EXISTS,
               "amenity": {"$exists": False},
               "place": {"$exists": False},
               "amenity": {"$exists": False},
                "shop": {"$exists": False},
              "tourism": {"$exists": False},
              "office": {"$exists": False} }))


# In[13]:


## Improvement 4.1
sbg.count_documents({"place": {"$exists": True}, "is_in":{"$exists": False}})


# In[14]:


dict(sbg.find_one({"address": {"$exists": True}, "place": {"$exists": False}, "address.street": {"$exists": False}}))


# In[15]:


## Improvement 4.2
node_id = dict(sbg.find_one({
                        "address": {"$exists": True}, 
                        "place": {"$exists": False}, 
                        "address.street": {"$exists": False}}))["id"]
list(sbg.find({
                    "class": "way",
                    "node_refs": {
                        "$elemMatch": {
                            "$eq": node_id
                        }}}))

