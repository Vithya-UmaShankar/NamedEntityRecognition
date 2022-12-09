# NamedEntityRecognition
This project is used to extract entities from a text through a custom NER(Named Entity Recognition). NER is a form of Natural Language Processing(NLP) and is used to identify and extract useful bits of information from text. In this project the custom NER was built using spacy.
At this point the project can recognize and extract things and players related to cricket.

<img width="1415" alt="Screenshot 2022-12-08 at 3 27 42 PM" src="https://user-images.githubusercontent.com/49974137/206417351-0d83cc4e-7ba2-4180-80ef-03b7a2ee2d08.png">


As of now the project can understand 
* Players (Even when they are referenced by their nicknames)
* Teams
* Organizations
* Stadiums
* Cities
* Batting Styles
* Bowling Styles

## Technologies
This project was created with
* Python 3.8
* Spring Boot 2.7
* Java 11
* Elasticsearch 8.2.2

## Setup
To run this project, clone it and do the following:
Locate the variable ```APP_PATH``` in ```src/main/java/com/example/NamedEntityRecognition/controller/MainController.java``` and change it so that it references your cloned project

```
public String APP_PATH = "/path/to/your/directory/" + "NamedEntityRecognition/Python/";
```

Run ```pip install -r python/requirements.txt``` from the root directory to install all the dependencies of python

Create a new index in ElasticSearch called ```ner```

## Usage
Once you clone this repo, you can run the springboot project and access it at ```localhost:8080```

The file ```CricketNamedEntityRecognitionTrain.py``` must be run first to train the model. After which you can run ```NamedEntityRecognition.py```. You wouldn't need to access it but if you need to it's at ```http://127.0.0.1:5000``` 

### Extract entity
```
curl -X POST "http://localhost:8080/api/v1/detectEntity" -H "Content-Type: application/x-www-form-urlencoded" -d "detectEntityText=That's it from the Eden Park! Dinesh Karthik shone with bat for India with his maiden fifty."
```

### Display a snapshot of training files
```
curl -X POST "http://127.0.0.1:8080/api/v1/display?sport=Cricket"
```

### Upload Training Files
```
curl -X POST "http://localhost:8080/api/v1/uploadFiles" -F files=@/pathtofile/BattingStyles.csv -F files=@/pathtofile/worldcities.csv -F files=@/pathtofile/BowlingStyles.csv -F files=@/pathtofile/CricketOrganizationsList.csv -F files=@/pathtofile/PlayersListWithNicknames.csv -F files=@/pathtofile/StadiumList.csv -F files=@/pathtofile/TeamList.csv
```

### Unload NER model from memory
```
curl "http://127.0.0.1:5000/terminate?sport=Cricket"
```

### Reload NER model
```
curl -X POST "http://127.0.0.1:5000/reload?sport=Cricket"
```
