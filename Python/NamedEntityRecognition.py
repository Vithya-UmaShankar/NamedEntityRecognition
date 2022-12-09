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


def getFileNames(sport):
    
    directorypath = os.path.join(dirpath, "CSV", sport)
    fileNames = []
    for f in os.listdir(directorypath):
        if(os.path.isfile(os.path.join(directorypath, f))):
            if(f.split(".")[1] == "csv"):
                fileNames.append(f.split(".")[0])
                
    return fileNames

@app.route('/reload', methods = ['POST'])
def loadModel():
    sport = request.args.get('sport')

    if sport == "Cricket":
        global nlpCricket
        nlpCricket = spacy.load(os.path.join(dirpath, "CricketNamedEntityRecognition"))
        return Response(status=200)
    else:
        return Response(status = 404)

@app.route('/terminate', methods = ['GET'])
def unloadModel():
    sport = request.args.get('sport')

    if sport == "Cricket":
        global nlpCricket
        nlpCricket = None

        return Response(status=200)

    else:
        return Response(status = 404)
    
@app.route('/elastic', methods = ['POST'])
def elastic():
    
    data = request.form["data"]
    sport = request.args.get('sport')

    text =[]
    startChar = []
    endChar = []
    entityText = []
    entityLabel = []
    data_dict = {}
        
    data = data.replace("{", "").replace("}", "")
    data = data.replace(data.split("startChar")[0],'"')
    splits = data.split("],")
    for ent in splits:
        ent = ent.replace("\"", "").replace("[", "").replace("]", "").replace(" ", "")
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
            entityLabel[i] : entityText[i],
            "sport": sport
        }
        es.index(index='ner', document=query) 
        i = i + 1

    
    return Response(status=200)

@app.route('/check', methods = ['GET'])
def check():
    check = (nlpCricket == None)
    
    return  str(check)
    
@app.route('/extract', methods = ['POST'])
def extractEntity():
    sport = request.args.get('sport')

    fileName = os.path.join(dirpath, "entityText.txt")
    
    startChar = []
    endChar = []
    entityText = []
    entityLabel = []
    
    f = open(fileName)
    text = f.read().replace("\xa0"," ")

    if sport == "Cricket":
        if nlpCricket == None:
            loadModel()
            
        doc = nlpCricket(text)

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
    
    sport = request.args.get('sport')
    fileNames = getFileNames(sport)
        
    for fileName in fileNames:
        df = pd.read_csv(os.path.join(dirpath, "CSV", sport, (fileName + ".csv"))).head(5)
        dfi.export(df,os.path.join(dirpath, "Images", sport, (fileName + ".jpg")))

    return Response(json.dumps(fileNames), status=200)

if __name__ == '__main__':

    dirpath = os.path.dirname(app.instance_path)
    nlpCricket = spacy.load(os.path.join(dirpath, "CricketNamedEntityRecognition"))

    es = Elasticsearch("https://localhost:9200",
                   ca_certs=False,
                   verify_certs=False,
                   http_auth=('elastic', '*XxotzsQktEZZ+9fGZi-'))
    app.run()
