#!/usr/bin/env python
# coding: utf-8

# ## Import Dependencies

# In[27]:


import pandas as pd
import numpy as np
import datetime
import re
import json
import spacy
import random
import os
from spacy.lang.en import English
from spacy.pipeline import EntityRuler
from spacy.training.example import Example


# ## Gather Training Data

# In[2]:


def load_data(file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return (data)


# In[3]:


def save_data(file, data):
    with open (file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# In[4]:


def load_csv(file):
    df = pd.read_csv(file)
    
    #Format Date Of Birth column string to Dates
    df["DOB"] = pd.to_datetime(df.Birthdate)

    #Drop columns with no values
    df = df[df['DOB'].notna()]

    #Get current date and time
    now = datetime.datetime.now()

    #Changed back wrong convertions. 26-2-56 is converted to 26-2-2056 instead of 26-2-1956
    df.loc[df['DOB'].dt.year >= now.year, 'DOB'] -= pd.DateOffset(years=100)

    #Get only current players
    df = df[(df['DOB'] >= "1970-01-01")]

    #Drop columns with no value
    df = df[df['NAME'].notna()]
    df = df[df['Full name'].notna()]

    #Form another df with just names
    df_split = df[["NAME", "Full name", "Nickname"]]
    
    return df_split


# In[5]:


def extract_names(df):
    names = df['NAME'].tolist()
    names.extend(df['Full name'].tolist())
    
    #Drop rows with empty nicknames
    df_result = df[df['Nickname'].notna()]
    names.extend(df_result['Nickname'].tolist())
    
    return names


# In[6]:


def generate_names(names):
    players_list = []
    for name in names:
        players_list.append(name.strip())

    for name in names:
        name = re.sub(' +', ' ', name).strip()
        name = clean_text(name) #Remove quotes and brackets surrounding the name
        split_name = name.split(" ")
        initial = ""
        half_name = ""
        for part_name in split_name[:-1]:
            initial = initial + " " + part_name[0].upper()
            nickname = initial + " " + split_name[-1:][0]
            players_list.append(nickname.strip())
            half_name = half_name + " " + part_name
            players_list.append(half_name.strip())

    return players_list


# In[7]:


def clean_text(text):
    cleaned = re.sub(r"[\(\[].*?[\)\]]", "", text)
    return (cleaned)


# In[8]:


def extract_nicknames(players_list, nicknames):
    for nickname in nicknames:
        nickname_list = nickname.split(",")
        for name in nickname_list:
            players_list.append(name.strip())
    
    return players_list


# In[9]:


def generate_player_patterns(file):
    df = load_csv(file)
    names = df['NAME'].tolist()
    names.extend(df['Full name'].tolist())
    players_list = generate_names(names)

    df_nickname = df[df['Nickname'].notna()]
    nicknames = df_nickname['Nickname'].tolist()
    players_list = extract_nicknames(players_list, nicknames)

    players_list = list(set(players_list))
    players_list.sort()
    
    if 'A' in players_list or 'a' in players_list:
        players_list.remove('A')
    
    if 'The' in players_list or 'the' in players_list or 'THE' in players_list:
        players_list.remove('The')
    
    if 'He' in players_list or 'he' in players_list or 'HE' in players_list:
        players_list.remove('He')
    
    if '' in players_list:
        players_list.remove('')

    return list(set(style_patterns(players_list)))


# In[10]:


def create_player_training_data(file, type):
    players_list = generate_player_patterns(file)
    
    if 'A' in players_list or 'a' in players_list:
        players_list.remove('A')
    
    if 'The' in players_list or 'the' in players_list or 'THE' in players_list:
        players_list.remove('The')
    
    if 'He' in players_list or 'he' in players_list or 'HE' in players_list:
        players_list.remove('He')
    
    if '' in players_list:
        players_list.remove('')
        
    patterns = []
    for name in players_list:
        pattern = {
            "label": type,
            "pattern": name
        }
        patterns.append(pattern)
    return patterns


# In[11]:


def generate_city_patterns(file):
    df = pd.read_csv(file)
    places = df['city'].tolist()
    places = list(set(list(places)))
    return list(set(style_patterns(places)))


# In[12]:


def create_city_training_data(file, type, patterns):
    places_list = generate_city_patterns(file)
    
    if 'a' in places_list:
        places_list.remove('a')
    
    for place in places_list:
        pattern = {
            "label": type,
            "pattern": place
        }
        patterns.append(pattern)
    return patterns


# In[13]:


def generate_stadium_patterns(file):
    df = pd.read_csv(file)
    stadiums = df['ground'].tolist()
    stadiums.extend(df['ground_long'].tolist())
    stadiums = list(set(list(stadiums)))
    #print(df)
    return list(set(style_patterns(stadiums)))


# In[14]:


def create_stadium_training_data(file, type, patterns):
    stadium_list = generate_stadium_patterns(file)
    
    for stadium in stadium_list:
        pattern = {
            "label": type,
            "pattern": stadium
        }
        patterns.append(pattern)
    return patterns


# In[15]:


def generate_organization_patterns(file):
    df = pd.read_csv(file)
    
    organizations = df['Organization'].tolist()

    df_organization = df[df['Short'].notna()]
    organizations.extend(df_organization['Short'].tolist())

    organizations = list(set(list(organizations)))

    return list(set(style_patterns(organizations)))


# In[16]:


def create_organization_training_data(file, type, patterns):
    organization_list = generate_organization_patterns(file)
        
    for organization in organization_list:
        pattern = {
            "label": type,
            "pattern": organization
        }
        patterns.append(pattern)
    return patterns


# In[17]:


def generate_batting_style_patterns(file):
    df = pd.read_csv(file)
    
    batting_shots_list = []
    batting_shots = df['BattingShots'].tolist()
    
    for batting_shot in batting_shots:
        batting_shots_list.append(batting_shot)
        batting_shots_list.append(batting_shot.lower())
        
    batting_shots_list = list(set(batting_shots_list))

    return list(set(style_patterns(batting_shots_list)))


# In[18]:


def create_batting_style_training_data(file, type, patterns):
    batting_style_list = generate_batting_style_patterns(file)
        
    for batting_style in batting_style_list:
        pattern = {
            "label": type,
            "pattern": batting_style
        }
        patterns.append(pattern)
    return patterns


# In[19]:


def generate_bowling_style_patterns(file):
    df = pd.read_csv(file)
    
    bowling_shots_list = []
    bowling_shots = df['BowlingShots'].tolist()
    
    for bowling_shot in bowling_shots:
        bowling_shots_list.append(bowling_shot)
        bowling_shots_list.append(bowling_shot.lower())
        
    bowling_shots_list = list(set(bowling_shots_list))

    return list(set(style_patterns(bowling_shots_list)))


# In[20]:


def create_bowling_style_training_data(file, type, patterns):
    bowling_style_list = generate_bowling_style_patterns(file)
        
    for bowling_style in bowling_style_list:
        pattern = {
            "label": type,
            "pattern": bowling_style
        }
        patterns.append(pattern)
    return patterns


# In[21]:


def generate_team_patterns(file):
    df = pd.read_csv(file)
    
    teams_list = []
    teams = df['Team'].tolist()
    
    for team in teams:
        teams_list.append(team)
        
    teams_list = list(set(teams_list))
    
    return list(set(style_patterns(teams_list)))


# In[22]:


def create_team_training_data(file, type, patterns):
    team_list = generate_team_patterns(file)
        
    for team in team_list:
        pattern = {
            "label": type,
            "pattern": team
        }
        patterns.append(pattern)
    return patterns


# In[23]:


def style_patterns(patterns):
    styled_patterns = []
    for pattern in patterns:
        styled_patterns.append(pattern)
        styled_patterns.append(pattern.upper())
        #styled_patterns.append(pattern.lower())
        styled_patterns.append(pattern.title())
        styled_patterns.append(pattern.capitalize())
        
    return styled_patterns


# In[24]:


def generate_rules(patterns):
    nlp = English()
    entity_ruler = nlp.add_pipe("entity_ruler")
    entity_ruler.initialize(lambda: [], nlp=nlp, patterns=patterns)
    nlp.to_disk(os.path.join(os.getcwd(), "CricketNamedEntityRecognition"))


# In[30]:


path = os.path.join(os.getcwd(), "CSV", "Cricket")
patterns = create_player_training_data(os.path.join(path, "PlayersListWithNicknames.csv"), "PLAYER")
patterns = create_city_training_data(os.path.join(path, "worldcities.csv"), "PLACE", patterns)
patterns = create_stadium_training_data(os.path.join(path, "StadiumList.csv"), "STADIUM", patterns)
patterns = create_organization_training_data(os.path.join(path, "CricketOrganizationsList.csv"), "ORGANIZATION", patterns)
patterns = create_batting_style_training_data(os.path.join(path, "BattingStyles.csv"), "BATTING", patterns)
patterns = create_bowling_style_training_data(os.path.join(path, "BowlingStyles.csv"), "BOWLING", patterns)
patterns = create_team_training_data(os.path.join(path, "TeamList.csv"), "TEAM", patterns)


# In[31]:


generate_rules(patterns)


# ## Buildig The Model

# In[32]:


text = """"	David Miller (64* off 31 balls) is the PLAYER OF THE MATCH for his match-winning innings! Miller says he has been working hard the last 4-5 years and understands the game well now. Adds that the chat was to hang in there, he was hitting well while Rassie was struggling so they tried to limit the dots and hit the loose balls. Shares that he has been around for quite some time and it gives him good confidence now. Mentions that wherever the team wants him to bat, he is happy to help and make a difference.

	Temba Bavuma, captain of South Africa says that they expected the wicket to get better at night and it did happen. Adds that the way Ishan Kishan batted, he made it look very easy and put their spinners under pressure and with the left-hand, right-hand combination it was difficult to bowl at them. Goes on to applaud Rassie and Miller for their efforts and mentions that they need to execute their plans a bit better while bowling and it may seem overly critical but that's what makes a difference. Says that Miller is a powerhouse and Rassie is a different player, he backs himself to hit the ball well after taking a bit of time and is happy with their efforts. Ends by saying that yes it is hot but it's about preparing for the game.

	Indian skipper, Rishabh Pant says that they had enough runs on the board but feels that they were off the ball and says David Miller and Rassie van der Dussen played brilliantly. Feels that the wicket got better in the second half and tells next time they will do better to execute their plans with the ball.

	Man of the moment, Rassie van der Dussen is up for a quick chat. He says he feels good, they had a good preparation. Adds the wicket was sticky but David Miller helped him a lot. Adds that he was a few boundaries away, the intent was clear and he just needed to hit a few out of the middle to get away. He sometimes take 30-40 balls and that is his gameplan that has worked for him in the last few years,and the management trust him as well. Informs Avesh Khan put him under a lot of pressure but Miller helped him from the other end. Shares that they had clear instructions and Dwaine Pretorius gave a great start. The key was not to panic and hang in there. Ends by saying, sometimes the strangest things that make a difference, seems like the game turned when he changed his bat.

	Earlier in the game, India were inserted into bat and after a quick-fire start, Ishan Kishan went on to score big to lay down the foundation for a big total. Shreyas Iyer, Rishabh Pant and especially Hardik Pandya played blistering cameos to take the final total to 211. The South African spinners were mostly inefficient but Keshav Maharaj did bowl well and picked up an important wicket. The pacers too had a mixed day but were good in patches of the game. The visitors need to go hard from the start to chase down the score and Dwaine Pretorius gave them the best start possible even after losing a wicket early in the Powerplay. After a sedate start, Rassie van der Dussen was able to change the momentum of his innings and along with David Miller made the chase look pretty straightforward in the end. Let's now head over for a few interviews…

	At the halfway mark, Ishan Kishan mentioned that 150 might have been a par score on this pitch and India would have been confident of defending the total. But given the dimensions of the ground and how the game works nowadays, no total is big enough and the Indian bowlers learned it the hard way. Bhuvneshwar Kumar was very good inside the Powerplay but whoever came on got hit. It was then Harshal Patel who turned the tide with the wicket of Dwaine Pretorius and after that Axar Patel and the others were able to keep a lid on the runs. Avesh Khan was expensive in his first over but bowled well when he came back on. Bhuvi and Harshal just didn't have an answer at the death for the well-set batters and Shreyas Iyer's dropped catch of Rassie when he was going nowhere might have been the turning point.

	The visitors have had a night to remember here in Delhi. With 212 needed to win, no one would have expected that they would be able to chase it down. But they had the experience and it showed in the most important moments of the game. After a quick start, skipper Temba Bavuma fell early. Dwaine Pretorius was sent in as a pinch-hitter and it worked wonders for South Africa inside the Powerplay. Once he was dismissed though, Quinton de Kock too fell. Rassie van der Dussen wasn't able to get going at all but David Miller did get a good start at the other end which just kept the visitors in the game. Rassie van der Dussen came alive though when it mattered the most and just smoked the bowlers to all parts in the last few overs. Both batters surpassed their individual fifties and put on a mammoth partnership of 131 runs to win the match for their team.

	It was quite a one-sided finals in the end! Gujarat probably wanted it a lot more than Rajasthan as the latter were just not as their best. They were well below par with the bat, despite being around 60 for 1 in the 8th over, they ended up with only 130. Yes, the likes of Pandya and Rashid bowled brilliantly but the batting and the shot selection was also not of the highest quality. 

	In the second half, Rajasthan needed early wickets, they did have a chance in the very first itself but they dropped Gill. They did manage to get a couple but that drop of Gill cost them dearly. A couple of partnerships is all that Gujarat needed and they got that. First it was Gill and Pandya and then Miller along with Gill. Shubman Gill was the mainstay in this innings and the rest played around him. 

	For Rajasthan, Boult and Prasidh Krishna bowled well but they needed to keep taking wickets and that was not the case. Yes, they did keep it quiet for a while but just could not get the wickets. There were half chances which they failed to take and when defending such totals, that need to be taken. Have to say, the better side won and Gujarat were the better side by a long way.  Stay tuned as there are interviews coming in a flurry…

	Mohammad Shami is up for a chat. He says they wanted a good start (the first ball dismissal of KL Rahul in the team's first game) and that just set up a template for a team. He wanted to serve on a good length and line and keep it simple. Adds that Saha has the abilities, he just needs opportunities. Saha joins him and says it was his fifth final but second on the winning side. Everyone said it is not a good squad but they have shown what they are capable of. 

	David Miller is up for a chat. He says it was a phenomenal journey. It is a collective effort and it is the best season he ever had. On Hardik Pandya, he says he has led the team fantastically throughout the seasons and feels this is the best season for him in the tournament. Matthew Wade joins him and says it is a relaxed environment, it is a family-type atmosphere and Hardik Pandya, and Rashid Khan was superb for them this season. Lauds Ashish Nehra as well. Tells that everyone got time in the ents and were given chances. On the crowd, he thanks and hopes to do it again next year. Lockie Ferguson joins as well. He says it feels good to win, is he happy for the boys. Adds that Hardik Pandya led them from the front and today he was a standout both with the bat and ball.

	Rashid Khan is up for a chat. He says they adjusted quickly, they needed to hit the right areas and everyone took the responsibility and bowled well. Adds he is very happy with how Gill played and he is very pleased with how he played. Gill says winning this tournament is as big as winning the World Cup and he is very pleased with them winning it. Rashid then says winning this tournament is one of the biggest achievements and you need to be prepared to win such tournaments. Adds, he feels their bowlers bowled really well and he felt anything under 150 was going to be a good target to chase down and they did chase it down.

	Rahul Tewatia is up for a chat. He says the environment was warm in the Qualifier 1 and they always wanted the finishers to end the game and with top order giving a good start. Adds their sole goal was to win the trophy and jokes saying, he won't sleep tonight. Shares that everyone were doubting them but the management trusted them. Tells that Hardik Pandya has given him the freedom to play his game. 

	Gary Kirsten says he is very happy for the guys and they put in a lot of hard work and it has been an amazing journey. States they were looking for a good balance in the auction but more than that, they were looking for versatile guys and that is what they got. States they put up a good bowling attack throughout the tournament, Sai Kishore was really good towards the end. Credits the way Pandya played and captained and he enjoyed working with him and he has been really engaging with the players and has played with a lot of responsibility. Ends by saying he enjoys his coaching and he loves working with Ashish Nehra.

	Hardik Pandya is the Player of the Match for his all-round performance both with the bat (34 runs off 30 balls) and with the ball (3/17) - He says he has worked very hard for it and at the right time he wanted to show what he has worked for and with the bowling point of view, he saved the best for the last. States if one hits the wicket hard, something was happening and he just wanted to hit the length right. States he would take the trophy rather than scoring quickly and for him his team is important and for his team, he needed to bat carefully. States when the auction was done, he knew he had to bat up the order and he has done this before and will do it ahead if needed.

	Jos Buttler is the Player of the Season - The Englishman says he is disappointed they could not take home the trophy and congratulates Hardik and Gujarat. States he reacts according to the game and he plays according to how the game wants him to. States he has huge trust in everyone and everyone has played well but today they came short and he just tries to react according to the game situation. Adds he is very grateful for the opportunity he got today, he is disappointed he lost this one and it has been a privilege to win the highest scorer.

	Kumar Sangakkara, the head coach of Rajasthan collects the runners-up medal - The Sri Lankan legend says they had a huge contribution from Jos Buttler, the two spinners, Prasidh Krishna also did well and almost everybody on the side contributed well. Adds the overall effort from everyone and the backing from the manager has been a lot. Adds he appreciates the journey but they need to be realistic about the things that could have been done and improve next year.

	Sanju Samson, the captain of Rajasthan says this season was special, he is proud of his team and there are a lot of good players, today was a day off but he is proud of his team. States right from the outset they wanted to have quality bowlers. States the roles were different for everyone and it was a decent season for them but there is a lot to learn. Ends by congratulating Hardik Pandya and Gujarat.

	The victorious skipper of Gujarat, Hardik Pandya says the whole support staff has been fantastic. Mentions he likes to play proper bowlers and the batters can chip in whenever required. Adds the batters need to put their hand up. Reckons it is the bowlers who win you the game. Adds it is always about becoming better and that is what they always try. Says he considers himself lucky, he has been in 5 finals and has won all 5 and to win it for the first time as captain is very special.

	The start to the chase was bright and breezy from Rajasthan. Yashasvi Jaiswal hammered Mohammed Siraj for 16 runs to set the tone, and then Jos Buttler capitalized. He started in the top gear, contrastingly to his last knock, and notched up a quickfire fifty. Rajasthan enjoyed a great Powerplay and brought the asking rate down to 6.5. Samson also played a handy knock, but his departure slowed the scoring rate. The victory though was never in doubt, and Rajasthan eventually crossed the line in the 19th over. Jos Buttler struck yet another century and stayed till the end.

	Bangalore will be deeply disappointed. Another season has gone and their trophy cabinet remains empty. They showed plenty of promise but failed to cross the last hurdle to get into the final. Their batting didn't operate at full strength once again. After the kind of start they had, Bangalore were in a good position to maximize the death overs but their innings nosedived and they managed just a below-par total. With the ball, the start from them was mediocre in the Powerplay and the writing was on the wall very early. They did try to create pressure later on but the damage was already done.

	Faf du Plessis, the captain of Bangalore, says that they were a few runs short. Feels that the start against the new ball was a bit tough but then they got the momentum. Admits that Rajasthan bowled very well in the end overs. Shares that there was plenty of bounce on the surface and it perhaps eased out in the second innings. Adds that he is proud of his team and thanks all the fans for supporting them. Talks about Harshal Patel, Wanindu Hasaranga and Dinesh Karthik for their performances this season, and expresses his disappointment for not making it to the final. Lauds the effort of the backroom staff and is grateful for the kindness shown to them. Further says that they have a few young boys who can turn into superstars and they have a great future. Signs off by thanking the Bangalore fans and says that the support they got is truly remarkable.

	Kumar Sangakkara, the director of cricket and head coach of Rajasthan, comes up for a chat! The Sri Lankan legend says that all the hard work and training paid off with this victory. Adds that the way guys picked themselves up after the last match was pretty special. Regarding Jos Buttler, Kumar replies that he has got some very potent strength and manoeuvres the bowling smartly, he is great against spin and has all the shots, and chooses his shots wisely. Adds that he can accelerate at any time which is a big bonus. Praises his bowlers and calls the entire bowling group amazing. Lauds Prasidh Krishna for the way he bounced back after his last match where he got hit for three sixes by David Miller and talks about the commitment of Obed McCoy whose mother is ill back home. For the Rajasthan spinners, Kumar replies that they have been running the show for them, and as a unit, they stood up in this match. Mentions about the auction strategy and tells that they worked hard in picking the players, and their core is a group of seasoned international players. Signs off by saying that they will look to do the basics right against Gujarat and the team that plays better on that evening will win.

	Sanju Samson, the victorious captain of Rajasthan, says that it was really tough for them after the last loss but they are used to bouncing back. Adds that the pitch was a bit sticky and helping the fast bowlers. Mentions that his fast bowlers executed the plans really well and they closed the innings superbly. Tells that they believed in their skills and that got them through. Smiles and says that toss plays a role definitely as the wicket plays differently in the second innings. On Obed McCoy, Samson replies that he is a tough character and very calm and composed who backs his strengths. Regarding Jos Buttler, Samson hopes that he has one more big knock left in him. Talks about the final of the first Indian T20 League and shares that he was very young at that time.   

	Jos Buttler (106* off 60 balls) collects the Player of the Match award! The Englishman says that he came in this season with great excitement and to get into the final is incredibly exciting. Adds that he has had a tournament of two halves and has had really honest conversations with the people close to him. Admits that he was feeling the pressure but he went to Kolkata a lot more relaxed. Shares that he always tries to react to the game situation. Shares that Kumar Sangakkara has advised him by saying that the longer he will stay there, the more runs will come. On his celebration after scoring a ton, Jos replies that after two years of playing on empty grounds, he was very excited in front of a capacity crowd. Talks about Shane Warne who was an influential figure for Rajasthan and say that the great man will be looking down on them with a lot of pride.

	Lucknow were always behind the eight ball as they were chasing a huge total and they were hampered down in the first over as Quinton de Kock got out. It was the stand between Hooda and Rahul that brought the impetus back as both played with calmness and control to keep the required run rate in check. Once Hooda fell, the pressure was on KL who tried his best to play the anchor role but when he tried to change the gears, he perished and after that, it was too hard for Lucknow to chase it down. 

	Harshal Patel was the hero for Bangalore! When Faf du Plessis wanted a wicket, he went to his key bowler and Harshal proved to be the game-changer. He was the most economical of all five bowlers! Other bowlers went for runs but came back at a crucial time to grab some wickets. Other than bowling and batting, Bangalore were on top in the fielding department as well, and to be honest, Lucknow's fielding kept them away from the victory line as well. 

	Earlier in the evening, we witnessed a masterclass from Rajat Patidar. He along with Dinesh Karthik set a huge target and gave the bowlers a lot to fight with. They were leaking runs at the beginning of the second innings but they fought back well and put a lid on the rid flow in the middle phase. In the end, Harshal Patel and Josh Hazlewood displayed their magic and defended the runs. Stay tuned for interviews... 

	KL Rahul is down for a chat. He says they let their selves down in the field, easy catches being dropped never helps the side, Patidar played a terrific knock and Bangalore were excellent in the field and they were poor. Mentions that they will take back a lot of positives, they have played well, they have a really young team, a lot of guys are under the age of 25 who have done well in patches but they have a lot of learnings to do, and they will keep getting better. On Mohsin Khan, he says that he has been good for them, he will only get better and he will get faster as well and he has a great future ahead of him.

	Harshal Patel is down for a chat. He says that his hand is healing superficially, but there is a slight issue inside. However, if he can bowl his 24 balls he is fine! Mentions that he had a lot of thought regarding his bowling in his mind considering they were playing in Mumbai which supports the batters, so he wanted to bowl hard lengths and he did see his stats which say that he goes for around 7 runs in an over when he bowls his hard lengths, so he stuck with that. States that it feels exceptional to go through and he can't express his emotions of what he felt when Mumbai beat Delhi, and he knew then that Bangalore would be a tough team to beat!

	Faf du Plessis, the winning skipper of Bangalore, says the guys put in a great performance, he is over the moon, Rajat Patidar played an exceptional knock, the way he played it just tells us there is a good head on those shoulders, it was one of the better hundreds he has seen. Mentions that he has got all the shots, and every time they were under pressure, Patidar came back stronger and played his shots. Adds that they were high on emotion and were very happy before the game and it was important to keep calm and have a clear mind during the game. States that Harshal Patel is the joker in the pack, he is a special guy in the team, and he always wants to bowl the important overs for Bangalore!

	Rajat Patidar (112* off 54 balls) is the Player of the match. He says he was just focusing to time the ball well and not hitting too hard. Adds that in the 5th over, facing Pandya, he started to execute well and he felt it might be something special for him. Tells that he wanted to cash in on this batting pitch. Shares he doesn't feel much pressure of dots as he can cover up later quickly. Mentions that he was not picked up in 2021 but he kept his focus throughout. 

	Gujarat are heading to their capital - AHMEDABAD, for the FINAL OF THE INDIAN T20 LEAGUE, 2022. What a season this has been for them. What a fairytale this has been, not many people gave them the chance at the start of the season but their performance has proved once again that this is a team game and if you click as a unit, it is very hard to stop you. Rajasthan, on the other hand, should keep their heads high. They were in the match right till the end and were probably the more fancied team going into the final over but it was just the 'Killer Miller' magic that took the game away from them. They have yet another chance to bounce back and they have played good cricket so far and would be looking to end on the right side of the result in Qualifier 2.

	This was yet another one of those classic Gujarat chases that we have been so used to seeing this season. The target was a big one and the stakes were high but they have nailed some fantastic chases this season and this is another one of those. They lost Saha in the first over but Gill and Wade kept the momentum on their side as they found boundaries at regular intervals in the Powerplay. However, Gill got run out in the 8th over in an unfortunate manner and Wade followed soon. The best thing about this chase was the required rate never got out of the hands as Miller and Pandya planned it superbly. The second-last over though brought the equation to 16 off 6 but Miller, as cool as ever, finished the chase with three towering sixes.

	Earlier in the game, Rajasthan managed to put a big score courtesy of a fantastic knock by Buttler. The Rajasthan skipper, Samson was the one who provided the momentum and overall, Rajasthan had an upper hand going into the innings break. For Gujarat, apart from Rashid Khan, all the bowlers were expensive but the Rajasthan bowlers too could not keep the scoring rate under check and in the end, Gujarat inched ahead by winning those crucial moments in a tight game.

	Sanju Samson, the captain of Rajasthan, says that they felt really good after putting in that kind of a total, as the wicket was sticky. Feels that they batted really well. Adds that it was a bit two-paced and the bounce was also uneven. Calls it a tough wicket to bat on, and feels that it was a great performance from their batters. Mentions that their 5-bowler strategy has worked so far and opines that the wicket got a bit easier in the second innings. Wants his team to come back stronger. Tells that they played well in this match as well but a few overs didn't go their way. Hopes for a good result in the next game.

	Shubman Gill (35 off 21 balls) comes up for a chat. The Gujarat opener says that Kolkata has always been nice to him and fortunately, he has ended on the winning side. Adds that batting at Eden Gardens is an opportunity you look forward to. Tells that they got off to a great start in the Powerplay. Shares that they expected the pitch to be a belter but it surprised them. Informs that the spinners were getting a little bit of grip. Further says that it's exciting, the team is new but the way they have come together is amazing. Regarding any pressure on him after Gujarat picked him in the draft, Gill replies that there wasn't any added pressure on him as they retained him on his past performance.

	Hardik Pandya, the victorious captain of Gujarat, says that he has started to balance things in his life. Adds that it's been difficult for him to manage his body, the bubble life, and his family has played a big role in making him a better cricketer. Tells that he is trying to be neutral at this moment and is really proud of all the boys. Shares that if you have good people around you, you tend to get good things. Further says that all the boys are backing each other, and that's the reason they have reached this stage. Mentions that it's all about respecting the game, he is proud of Miller and during the chase, they wanted to finish the game and not leave it for the others. Regarding batting at number 4, Hardik replies that it all depends on what his team wants from him. Tells that they appreciate all the knocks, no matter how small or big, and signs off by saying that winning the trophy is a dream.

	David Miller is the Player of the Match for his incredible 68* off just 38 balls. Regarding what has changed for him this season, the South African replies that he has got opportunities and a good role in the team, and that's the reason for his success. He is enjoying his role and is understanding his game a little better. Further says that he wants to keep everything closer to his game plan. Tells that he just backed himself and went for the big shots. Adds that he has played for different teams and knew a few players already in Gujarat. Shares that the first win that they had was close, and that brought them together. On his plans for the final over, Miller says that you need to control what you can and cannot think too much ahead. Further says that if it's in your area, you have to capitalize as it's all about taking all your opportunities.
    
	BCCI is a stupid organization and is a load of stupid people running it.

	17.3: Ravi Bishnoi to Asif Ali, DROPPED! Fuller and on off, Asif Ali looks to slog sweep it but mistimes it completely. The ball goes high up in the air towards short third man and Arshdeep Singh drops a dolly. Can this be a turning point in the game?
    
	17.3: Ravi Bishnoi to Asif Ali, WIDE! Short and turning well down the leg side, Asif Ali looks to pull but misses. The ball goes way down the leg side and a wide is called. Rishabh Pant thinks he heard a sound and Rohit Sharma does review it. The third umpire checks UltraEdge and there is a slight murmur as the ball passes the gloves and the third umpire takes his time. In the end, he concludes that it is too tight to be deemed as a nick and stays with the on-field decision.
    
	16.5: Hardik Pandya to Mohammad Rizwan, OUT! CAUGHT! Hardik Pandya has got the big fish here and the crowd is jumping in joy. Mohammad Rizwan walks out after an amazing knock. Coming to the delivery, this one lands fuller and on off, Mohammad Rizwan looks to loft it but doesn't get the power right. The ball goes high up in the air towards long off. Suryakumar Yadav settles under it and pouches it easily. 35 needed from 19 now.
    
	That is all we have from this exciting game. The action in the Indian T20 League continues on Tuesday, the 26th of April with Bangalore taking on Rajasthan at the ZAC Stadium in Pune. That match will begin at 7.30 pm IST (2 pm GMT). You can join us in advance for the build-up. Until then, it's goodbye and cheers!
    
	39.6: H Pandya to I Wasim, A swing and a miss to end the farce. INDIA WON BY 89 RUNS VIA DLS METHOD.
    
	37.1: Y Chahal to I Wasim, Wide! Googly but on the shorter side and way wide outside off, Wasim leaves.
    
	36.3: J Bumrah to I Wasim, Perfect yorker, around middle, Imad initially lines up for a slog but at the last moment, adjusts to drag it towards square leg."""


# In[33]:


def create_train_model(model, text):
    doc = model(text)
    results = []
    entities = []
    for ent in doc.ents:
        entities.append((ent.start_char, ent.end_char, ent.label_))
    
    if len(entities) > 0:
        results = [text, {"entities": entities}]

        return results


# In[34]:


nlp = spacy.load(os.path.join(os.getcwd(), "CricketNamedEntityRecognition"))
text_para = text.split("\n")
TRAIN_DATA = []
for para in text_para:
    results = create_train_model(nlp, para)
    if results != None:
        TRAIN_DATA.append(results)

save_data(os.path.join(os.getcwd(), "CricketNamedEntityRecognitionTrainingData.json"), TRAIN_DATA)


# ## Training The Model

# In[35]:


def train_model(TRAIN_DATA, iterations):
    nlp = spacy.blank("en")
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last= True)
    for text, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
            print(ent[2])

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        for itn in range(iterations):
            print("Starting iterations" + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                
                nlp.update(
                        [example],  
                        drop = 0.2,  
                        sgd = optimizer,
                        losses = losses
                    )
                print(losses)
        return(nlp)


# In[36]:


TRAIN_DATA = load_data(os.path.join(os.getcwd(), "CricketNamedEntityRecognitionTrainingData.json"))
nlp = train_model(TRAIN_DATA, 20)
nlp.to_disk(os.path.join(os.getcwd(), "CricketNamedEntityRecognitionModel"))


