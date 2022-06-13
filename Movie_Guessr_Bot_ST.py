#This programm was made by AtoriYKZ (PINPIN Pierrick)
#This is a bot Twitter which makes you guessing synopsis of a movie, an actor, a director
#Twitter: https://twitter.com/Pierrick_YKZ
#Linkedin: https://www.linkedin.com/in/pierrick-pinpin-1b83b81a4/


#Imports
import tweepy as tp
import imdb
import random as rd
import nltk
nltk.download('punkt')
from nltk.tokenize import WhitespaceTokenizer
import csv
import requests
import os

"""
#nltk specials
nltk.download("wordnet", "D:/Projets Perso/Twitter Bot/Movie Guessr/Code Python/nltk_data")
nltk.data.path.append('D:/Projets Perso/Twitter Bot/Movie Guessr/Code Python/nltk_data/')
"""


#Fonctions Twitter:

#Connexion Twitter
def Twitter_api():
    apikey= "********************************"
    apiKeySecr= "**************************************"
    accToken= "**************************************************"
    accTokenSecr= "****************************************************"

    auth= tp.OAuthHandler(apikey, apiKeySecr)
    auth.set_access_token(accToken, accTokenSecr)


    api= tp.API(auth)

    try:
        api.verify_credentials()
        print("Connected")
    except:
        print("ERROR: Not connected")

    return(api)

#Vérifie si la taille du text est la bonne pour un tweet
def Tweet_len(text):

    tmp= ""
    if(text is not None):
        sent= nltk.sent_tokenize(text)

        if(len(text)>280):
            i= 0
            while(len(tmp+" "+sent[i+1])<280):
                tmp= tmp+" "+sent[i]
                i= i+1
        
        else:
            tmp= text
    
    else:
        tmp=""
    
    return(tmp)

#Tweet le text
def Tweet(text):

    api = Twitter_api()
    try:
        status= api.update_status(status= text)
        print("Tweet sent")
        print("Text: " + text)
        return(status.id)
    except:
        print("Tweet is not sent")
        pass  

#Tweet the picture(url) and a text(message)
def Tweet_pic(url, message):
    
    api = Twitter_api()
    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)

        status= api.update_status_with_media(status=message, filename= filename)
        os.remove(filename)
        print("Tweet sent")
        return(status.id)
    else:
        print("Unable to download image")

#Reply to the tweet(id tweet)
def Tweet_reply(tweet_id, text):

    api = Twitter_api()
    try:
        api.update_status(status= text, in_reply_to_status_id= tweet_id, auto_populate_reply_metadata=True)
        print("The message: ", text, "is posted in reply to the tweet id: ", tweet_id)
        
    except:
        print("No tweet corresponds to the current condition")

#Return the replies of a tweet with its user's name and the id of the tweet
def get_replies(name, tweet_id):
        
    api = Twitter_api()
    replies=[]
    users_id=[]
    users_names=[]
    
    for tweet in tp.Cursor(api.search_tweets, q='to:'+name, result_type='recent').items(10000):
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if (tweet.in_reply_to_status_id_str==tweet_id):
                replies.insert(0,tweet.text)
                users_id.insert(0, tweet.id)
                users_names.insert(0, tweet.user.screen_name)
    dict_users=dict(zip(users_names, users_id))
    dict_replies= dict(zip(users_names, replies))

    return(dict_replies, dict_users)






#Fonctions IMDbpy:


#Return un dict(title: movie_id) du top 250 IMDb
def top250():

    ia= imdb.Cinemagoer()
    top250= ia.get_top250_movies()
    dict= {}
    for k in range(len(top250)):
        dict[top250[k].get("title")]= top250[k].movieID
    return(dict)


#Return le titre d'un film random non déja posted PARA: liste des films dans laquelle choisir
def rd_movie(movies_title_data):

    ia= imdb.Cinemagoer()
    rd_index= rd.randint(0,len(movies_title_data))
    rd_mv= movies_title_data[rd_index]


    boo= Verif_csv("Movie posted.csv", rd_mv)
    while(boo== True):
        rd_index= rd.randint(0,len(movies_title_data))
        rd_mv= movies_title_data[rd_index]
        boo= Verif_csv("Movie posted.csv", rd_mv)
    return(rd_mv)


#Return le synopsis d'un film selon son id
def get_synopis(id_movie):

    ia= imdb.Cinemagoer()
    movie = ia.get_movie(id_movie)
    tmp="Synopsis:"
    if(movie.get('plot') is not None):
        plot= movie.get('plot')[0]
        sent= nltk.sent_tokenize(plot)
        print("Plot:" + plot)

        if(len(plot)>280):
            i=0
            while(len(tmp+" "+sent[i+1])< 280):
                tmp= tmp+" "+sent[i]
                i= i+1
            supp= sent[-1]
            tmp= tmp.replace(supp,'') 
        
        else:
            tmp= tmp+" "+plot
            #supp= sent[-1]
            #tmp= tmp.replace(supp,'') 
        
        if(tmp== "Synopsis:"):
            tmp=""

    else:
        tmp= ""

    return(tmp)


#ACTORS

#Retourne un tuple(name, id) d'un random actor
def rd_actor():

    ia = imdb.IMDb() 

    dict250= top250()
    title250= []

    for key in dict250.keys():
        title250.append(key)

    rd_mv= rd_movie(title250)
    mv_id= dict250.get(rd_mv)

    movie= ia.get_movie(mv_id)
    cast= movie['cast']

    dict_actors={}
    for per in cast:
        
        dict_actors[per['name']]= per.personID

    actors= []
    for k in dict_actors.keys():
        actors.append(k)

    rd_index= rd.randint(0,3)
    act_name= actors[rd_index]
    act_id= dict_actors[act_name]

    boo= Verif_csv("Actor posted.csv", act_name)
    while(boo== True):

        rd_mv= rd_movie(title250)
        mv_id= dict250.get(rd_mv)

        movie= ia.get_movie(mv_id)
        cast= movie['cast']

        dict_actors={}
        for per in cast:
            
            dict_actors[per['name']]= per.personID

        actors= []
        for k in dict_actors.keys():
            actors.append(k)

        rd_index= rd.randint(0,3)
        act_name= actors[rd_index]
        act_id= dict_actors[act_name]
        boo= Verif_csv("Actor posted.csv", act_name)

    return(act_name, act_id)


#Return le lien du headshot d'un acteur selon son id
def Actor_headshot(act_id):

    ia = imdb.IMDb() 
    actor= ia.get_person(act_id)
    ok= False
    try:
        pic= actor['full-size headshot']
        ok= True
        return(pic, ok)
    except:
        ok= False
        pass

        return("", ok)



#DIRECTORS

#Return a dict of nb movies from the director(dir_id) // dict_mv={title : id} 
def get_director_movie(nb, dir_id):

    ia = imdb.IMDb()

    dict_mv={}
    dir_info= ia.get_person_filmography(dir_id)
    tmp= dir_info['data']['filmography']['director']
    for i in range(len(tmp)-1, len(tmp)-nb-1, -1):
        title= str(dir_info['data']['filmography']['director'][i])
        id= dir_info['data']['filmography']['director'][i].movieID
        dict_mv[title]= id
    return(dict_mv)

#Return a dict of directors (name, id) with an id of a movie
def get_director_id(mv_id):
    
    ia = imdb.IMDb()

    movie= ia.get_movie(mv_id)
    dict_directors={}
    directors= movie['director']

    for dir in directors:
        dict_directors[dir]= dir.personID
    
    return(dict_directors)
        
#Return the name and the id of a random director
def rd_director():

    ia = imdb.IMDb() 

    dict250= top250()
    title250= []
    for key in dict250.keys():
        title250.append(key)

    rd_mv= rd_movie(title250)
    mv_id= dict250.get(rd_mv)
    directors= get_director_id(mv_id) #dict

    directors_names= list(directors.keys())
    directors_id= list(directors.values())

    dir_name= directors_names[0]
    dir_id= directors_id[0]

    boo= Verif_csv("Director posted.csv", dir_name)
    while(boo== True):

        rd_mv= rd_movie(title250)
        mv_id= dict250.get(rd_mv)
        directors= get_director_id(mv_id) #dict

        directors_names= list(directors.keys())
        directors_id= list(directors.values())

        dir_name= directors_names[0]
        dir_id= directors_id[0]
        boo= Verif_csv("Director posted.csv", dir_name)

    return(dir_name, dir_id)











#Fonctions CSV

#Add an element(ans) to the file.csv(file)
def Add_ans_csv(file, ans):
    with open(file, 'w+', newline='') as f:
        obj = csv.writer(f)
        for i in ans:
            obj.writerow(i)

#Ajoute 1 titre de film et son ID
def Add_movie_posted(title, id):

    mv_posted[title]= id
    for k, v in mv_posted.items():
        title_posted.append(k)
        id_posted.append(v)
        mv_posted_list.append((k,v))

    return(mv_posted, title_posted, id_posted, mv_posted_list)

#Ajoute l'acteur aux variables(list)
def Add_actor_posted(name, id):

    act_posted[name]= id
    for k, v in act_posted.items():
        act_name_posted.append(k)
        act_id_posted.append(v)
        act_posted_list.append((k,v))

    return(act_posted, act_name_posted, act_id_posted, act_posted_list)


def Add_director_posted(name, id):

    dir_posted[name]= id
    for k, v in dir_posted.items():
        dir_name_posted.append(k)
        dir_id_posted.append(v)
        dir_posted_list.append((k,v))

    return(dir_posted, dir_name_posted, dir_id_posted, dir_posted_list)

#Add the list to the file.csv
def Add_posted_csv(file, list):

    with open(file, 'a+', newline='') as f: 
        ecrire=csv.writer(f)                      
        for i in list:
            boo= Verif_csv(file, i[0])
            if(boo== False):                             
                ecrire.writerow(i)  
             
def Add_points_csv(file, list):

    with open(file, 'a+', newline='') as f: 
        ecrire=csv.writer(f)                      
        for i in list:
            boo= Verif_csv(file, i[0])
            if(boo== False):                             
                ecrire.writerow(i)  



#Return une liste des éléments dans le csv
def Read_csv(file):

    read_list=[]
    with open(file, 'r') as f:
        obj = csv.reader(f)
        for ligne in obj:
            read_list.append(ligne)
    return(read_list)

#Vérifie si le title/ ID movie est dans le CSV ou non
def Verif_csv(file, what):
    
    inside= False
    read_list= Read_csv(file)

    verif_list=[]

    for l in read_list:
        for i in l:
            verif_list.append(i)

    if (what in verif_list):
        inside= True
    else:
        inside= False
    
    return(inside)











#Fonctions usuelles

#Return the key of a dict with a dict and a value
def get_key(dict, val):
    for key, value in dict.items():
         if val == value:
             return key
 













#Fonctions pour faire deviner:

#Synopsis:
#Tweet the synopsis of a random movie
def Guess_Synopsis():
    
    dict250= top250()
    title250= []
    for key in dict250.keys():
        title250.append(key)

    rd_mv= rd_movie(title250)
    mv_id= dict250.get(rd_mv)

    Add_movie_posted(rd_mv, mv_id)
    #mv_posted_list.append((rd_mv, mv_id))
    Add_posted_csv("Movie posted.csv", mv_posted_list)

    synopsis= get_synopis(mv_id)
    tweet_id= Tweet(synopsis)

    print(rd_mv, mv_id)
    ans=[[rd_mv, tweet_id]]
    print("The answer is: ", ans)
    Add_ans_csv("Answer tmp.csv", ans)



#Actor:
#Tweet the headshot of a random actor
def Guess_Actor():

    rd_act= rd_actor()
    actor_name= rd_act[0]
    actor_id= rd_act[1]
    
    Add_actor_posted(actor_name, actor_id)
    Add_posted_csv("Actor posted.csv", act_posted_list)

    tuple= Actor_headshot(actor_id)

    while(tuple[1]== False):

        rd_act= rd_actor()
        actor_name= rd_act[0]
        actor_id= rd_act[1]
        
        Add_actor_posted(actor_name, actor_id)
        Add_posted_csv("Actor posted.csv", act_posted_list)

        tuple= Actor_headshot(actor_id)

    tweet_id= Tweet_pic(tuple[0], "Guess this actor")

    print(actor_name, actor_id)
    ans=[[actor_name, tweet_id]]
    print("The answer is: ", ans)
    Add_ans_csv("Answer tmp.csv", ans)



#Director
#Tweet a list of movies from a random director
def Guess_Director():

    
    tmp= rd_director()
    dir_name= tmp[0]
    dir_id= tmp[1]

    Add_director_posted(dir_name, dir_id)
    Add_posted_csv("Director posted.csv", dir_posted_list)
    dict_mv= get_director_movie(3, dir_id)

    titles= list(dict_mv.keys())
    id= list(dict_mv.values())

    text= "Who directed these films: " + "\n" + "\n" + "- " + str(titles[0]) + "\n" + "- " + str(titles[1]) + "\n" + "- " + str(titles[2])
    tweet_id= Tweet(text)

    print(dir_name, dir_id)
    ans=[[dir_name, tweet_id]]
    Add_ans_csv("Answer tmp.csv", ans)
    print("The answer is: ", ans)
    











#Function for results of the guess-1:
def Result_day():
    
    answers= Read_csv("Answer tmp.csv")
    answer= answers[0][0]
    tweet_id= answers[0][1]
    print("Expected answer: ", answer)
    tuple_temp= get_replies("Movie_Guessr", tweet_id)
    text="" 








    dict_replies= tuple_temp[0] #dict_replies
    dict_users= tuple_temp[1] #dict_users

    winners=[]

    
    for rep in dict_replies.values():
        if(rep== answer):
            w_name= get_key(dict_replies, rep)
            winners.append(w_name)
            


    
    #Add to the csv (id, name, points)
    users_list= []
    users_names=[]
    users_id=[]
    users_points=[]
    result= Read_csv("Points.csv")
    dict_points={}
    for line in result:
        dict_points[line[1]]= line[2]

    for id in dict_users.values():
        users_id.append(id)
        name= get_key(dict_users, id)
        users_names.append(name)
        prep= dict_replies[name]

        #Verifie que l'id est dans le csv
        if(prep==answer):
            boo= Verif_csv("Points.csv", id)
            if(boo== True):
                point= int(dict_points[name])
                users_points.append(point)
            else:
                point= 1
                users_points.append(point)
        else:
            boo= Verif_csv("Points.csv", id)
            if(boo== True):
                point= int(dict_points[name])
                users_points.append(point)
            else:
                point= 0
                users_points.append(point)
    
    for k in range(len(users_id)):
        users_list.append([users_id[k], users_names[k], users_points[k]])
    
    Add_points_csv("Points.csv", users_list)

    if(not winners):
        text= "Nobody wins ! Try today !"
    if(len(winners)==1):
        text= "The correct answer was: " + answer + "\n" + "@" + winners[0] + " wins ! Congratulations !"
    if(len(winners)==2):
        text= "The correct answer was: " + answer + "\n" + "@" + winners[0] + " and " + "@" + winners[1] + " win ! Congratulations !"
    if(len(winners)>2):
        print(len(winners))
        text= "The correct answer was: " + answer + "\n" +"Last session's fastest winners are: " + "\n" + "\n" + "@" + str(winners[0]) + "\n" + "@" + str(winners[1]) + "\n" + "@" + str(winners[2])
        


    msg= Tweet_len(text)
    Tweet_reply(tweet_id, msg)


#MAIN
#Points
tmp= open('Points.csv','a+')
tmp.close()


#Results:
tmp_csv = open('Answer tmp.csv','a+')
tmp_csv.close()


tmp_csv= Read_csv("Answer tmp.csv")

if(not tmp_csv):
    print("Answer CSV file is empty")
    
    print(tmp_csv)
else:
    print("The result is: ", tmp_csv)
    Result_day()





#INITIALISATIONS
#Movies
mv_posted_list = open('Movie posted.csv','a+')
mv_posted_list.close()

mv_posted_list= Read_csv("Movie posted.csv")
title_posted=[]
id_posted=[]
mv_posted={}

if(not mv_posted_list):
    print("Empty file")
    print("mv_posted_list: ", mv_posted_list)
    print("title_posted: ", title_posted)
    print("id_posted: ", id_posted)

else:
    for i in mv_posted_list:
        title_posted.append(i[0])
        id_posted.append(i[1])

    mv_posted= dict(zip(title_posted, id_posted))

#Actors
act_posted_list = open('Actor posted.csv','a+')
act_posted_list.close()

act_posted_list= Read_csv("Actor posted.csv")
act_name_posted=[]
act_id_posted=[]
act_posted={}

if(not act_posted_list): #PB
    print("Empty file")
    print("act_posted_list: ", act_posted_list)
    print("act_name_posted: ", act_name_posted)
    print("act_id_posted: ", act_id_posted)

else:
    for i in act_posted_list:
        act_name_posted.append(i[0])
        act_id_posted.append(i[1])

    act_posted= dict(zip(act_name_posted, act_id_posted))

#Directors
dir_posted_list = open('Director posted.csv','a+')
dir_posted_list.close()

dir_posted_list= Read_csv("Director posted.csv")
dir_name_posted=[]
dir_id_posted=[]
dir_posted={}

if(not dir_posted_list):
    print("Empty file")
    print("dir_posted_list: ", dir_posted_list)
    print("dir_name_posted: ", dir_name_posted)
    print("dir_id_posted: ", dir_id_posted)

else:
    for i in dir_posted_list:
        dir_name_posted.append(i[0])
        dir_id_posted.append(i[1])

    dir_posted= dict(zip(dir_name_posted, dir_id_posted))






#Random function to guess
func= rd.randint(0,2)

if(func==0):
    Guess_Synopsis()
    print("Guess synopsis")
 

if(func==1):
    Guess_Actor()
    print("Guess actor")


if(func==2):
    Guess_Director()
    print("Guess director")



