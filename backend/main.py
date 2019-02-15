from flask import Flask, render_template, request
from pymongo import MongoClient
import urllib
from random import randint, shuffle
import math

PASSWORD=urllib.parse.quote("n!5HtH@1999")
mdburl="mongodb://nisinghal:"+PASSWORD+"@manateematinees-shard-00-00-0xodo.mongodb.net:27017,manateematinees-shard-00-01-0xodo.mongodb.net:27017,manateematinees-shard-00-02-0xodo.mongodb.net:27017/test?ssl=true&replicaSet=ManateeMatinees-shard-0&authSource=admin&retryWrites=true"
client = MongoClient(mdburl)
db=client.MatineesDB
movieInfo = list(db.MatineeInfo.find())
movieRating = db.MatineeRating
K=20
N=100
movies_list = movieInfo[:K]
user_ratings = {}
others_ratings = [{} for i in range(N)]
app = Flask(__name__)

#initialisation
@app.route('/init')
def init():
    for i in range(N):
        dummyUser={}
        global others_ratings
        for movie in movieInfo:
            dummyUser[str(movie["_id"])]=randint(1,6)
            others_ratings[i][str(movie["_id"])] = dummyUser[str(movie["_id"])]
        MovRateID = movieRating.insert_one(dummyUser).inserted_id
    return "Ratings initialised!"

# provide user a list of k movies 
@app.route('/')
def movieList():
    movienames = [movie["name"] for movie in movies_list]
    return render_template("index.html", names=movienames)

# accept rating of k movies
@app.route('/rate', methods=['POST', 'GET'])
def rate():
    rated_movies = request.form
    global user_ratings
    for i in range(K):
        user_ratings[movies_list[i]["_id"]] = rated_movies["rate"+str(i+1)]
    return render_template("method.html")

# recommend k movies  
#technique 1
@app.route('/recommendation/1')
def rec1():
    global user_ratings, others_ratings
    similarity_scores = [0 for i in range(len(others_ratings))]
    num = 0
    den1 = 0
    den2 = 0
    for i in range(N):
        for key in others_ratings[i].keys():
            num += (user_ratings[key] * others_ratings[i][key])
        for key in others_ratings[i].keys():
            den1 += (user_ratings[key] * user_ratings[key])
        for key in others_ratings[i].keys():
            den2 += (others_ratings[i][key] * others_ratings[i][key])
        similarity_scores[i] = num / math.sqrt(den1 * den2)
    highest = 0
    highest_score = similarity_scores[0]
    for i in range(N):
        if similarity_scores[i] > highest_score:
            highest = i
            highest_score = similarity_scores[i]
    rates = others_ratings[i]
    movs = ["" for i in range(K)]
    for i in range(K):
        highest = 0
        highest_score = 0
        ind = 0
        for j in rates.keys():
            if rates[j] > highest_score and j not in user_ratings and str(j) not in movs:
                highest = j
                highest_score = rates[j]
        movs[i] = str(j)
    nms = ["" for i in range(K)]
    for i in range(K):
        for mvi in movies_list:
            if mvi["_id"] == movs[i]:
                nms[i] = mvi["name"]
    return str(nms)

#technique 2
@app.route('/recommendation/2')
def rec2():
    return 'Hello, World!'

#technique 3
@app.route('/recommendation/3')
def rec3():
    return 'Hello, World!'

if __name__ == '__main__':
   app.run(debug=True)