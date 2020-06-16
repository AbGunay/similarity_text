from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.Similarity
users = db["Users"]

def userExist(username):
    if users.find({"Username":username}).count() == 0:
        return False
    else:
        return True

class Register(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData['Username']
        password = postedData['password']
        # if userExist(username):
        #     retJson = {
        #     "status":301,
        #     "msg":"User exist"
        #     }
        #     return jsonify(retJson)
        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
        users.insert({
        "Username":username,
        "Password":password,
        "Tokens":6})

        retJson = {
        "status":200,
        "msg":"Succesfully signed up"
        }
        return jsonify(retJson)

def countTokens(username):
    tokens = users.find({"Username":username})[0]["Tokens"]
    return tokens

class Detect(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["Username"]
        password = postedData["password"]
        text1 = postedData['text1']
        text2 = postedData['text2']

        num_tokens = countTokens(username)
        if num_tokens == 0:
            retJson = {
            "statuscode":303,
            "msg":"You are out of token"
            }
            return jsonify(retJson)

        nlp = spacy.load("en_core_web_sm")
        text1 = nlp(text1)
        text2 = nlp(text2)
        ratio = text1.similarity(text2)
        retJson = {
        "ratio":ratio,
        "status":200,
        "msg":"Similarity Calculated"
        }

        current_tokens = countTokens(username)
        users.update({
        "Username":username
        },{
            "$set":{
                "Tokens":current_tokens-1
            }
        })
        return jsonify(retJson)

api.add_resource(Register, '/register')
api.add_resource(Detect, '/detect')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
