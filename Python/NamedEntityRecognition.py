import json
from flask import request, Flask, Response

import spacy
import os
import sys
from datetime import datetime
from elasticsearch import Elasticsearch
import pandas as pd
import numpy as np
import dataframe_image as dfi

app = Flask(__name__)


@app.route('/reload', methods = ['POST'])
def loadModel():
    global nlp
    nlp = spacy.load(os.path.join(dirpath, "NamedEntityRecognition"))
    return Response(status=200)


@app.route('/terminate', methods = ['GET'])
def unloadModel():
    global nlp
    nlp = None
    return Response(status=200)


@app.route('/elastic', methods = ['POST'])
def elastic():
    
    data = request.form["data"]

    startChar = []
    endChar = []
    entityText = []
    entityLabel = []
    data_dict = {}
    
    data = data.replace("{", "").replace("}", "")
    splits = data.split("],")
    for ent in splits:
        ent = ent.replace("\"", "").replace("[", "").replace("]", "")
        key_split = ent.split(":")
        values = key_split[1].split(",")
        if key_split[0] == "startChar" or key_split[0] == "endChar":
            i = 0
            for val in values:
                values[i] = int(val)
                i = i + 1
        data_dict[key_split[0].strip()] = values
        
    startChar = data_dict["startChar"]
    endChar = data_dict["endChar"]
    entityText = data_dict["entityText"]
    entityLabel = data_dict["entityLabel"]


    #Adding Entity
    i = 0 
    for i in range(len(startChar)):
        query = {
            entityLabel[i] : entityText[i]
        }
        es.index(index='index11', document=query) 
        i = i + 1

    
    return Response(status=200)

@app.route('/check', methods = ['GET'])
def check():
    check = (nlp == None)
    
    return  str(check)
    
@app.route('/extract', methods = ['POST'])
def extractEntity():
    data = request.form["data"].replace("'","").replace("{","").replace("}","")

    arg_dict = {}
    data_args = data.split(",")
    for data_arg in data_args:
        parameters = data_arg.split(":")
        arg_dict[parameters[0].strip()] = parameters[1].strip()

    fileName = arg_dict.get("fileName")

    startChar = []
    endChar = []
    entityText = []
    entityLabel = []
    
    f = open(fileName)

    if nlp == None:
        loadModel()

    text = f.read().replace("\xa0"," ")
    doc = nlp(text)
    for ent in doc.ents:
        startChar.append(ent.start_char)
        endChar.append(ent.end_char)
        entityText.append(ent.text)
        entityLabel.append(ent.label_)

    result = {}
    result["text"] = text
    result["startChar"] = startChar
    result["endChar"] = endChar
    result["entityText"] = entityText
    result["entityLabel"] = entityLabel

    return Response(json.dumps(result), status=200)


@app.route("/display", methods = ["POST"])
def displayCSV():
   fileNames = ["PlayersListWithNicknames", "worldcities", "StadiumList", "CricketOrganizationsList", "BattingStyles", "BowlingStyles", "TeamList"]
   for fileName in fileNames:
      df = pd.read_csv(os.path.join("Tensorflow", "Projects", "NamedEntityRecognition", "CSV", (fileName + ".csv"))).head(5)
      dfi.export(df,os.path.join("Tensorflow", "Projects", "NamedEntityRecognition", "Images", (fileName + ".jpg")))
      
   return Response(json.dumps(fileNames), status=200)

if __name__ == '__main__':
    dirpath = os.path.join("/", "Users", "vithya", "Programs", "Python")
    nlp = spacy.load(os.path.join(dirpath, "NamedEntityRecognition"))
    
    es = Elasticsearch("https://localhost:9200",
                   ca_certs=False,
                   verify_certs=False,
                   http_auth=('elastic', '*XxotzsQktEZZ+9fGZi-'))
    app.run()
