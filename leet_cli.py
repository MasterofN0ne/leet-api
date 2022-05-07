import random
from re import A
import click
import pickle
from datetime import datetime, timedelta
import requests
import pymongo
from pymongo import MongoClient 
from dotenv import load_dotenv, find_dotenv
import os
import pprint
from passlib.hash import pbkdf2_sha256
from flask import session

load_dotenv(find_dotenv())
password = os.environ.get("MONGODB_PASSWORD")

connection_string = f"mongodb+srv://masterofsome:{password}@leetapp.y69mx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client["leetUserDB"]
leetData = db["leetDataDB"]
leetUser = db["leetUserDB"]

BASE = "http://127.0.0.1:5002/"

def put_request(commit_dict):
    response = requests.put(BASE + f"leet-api/leet/{commit_dict['leet_id']}", commit_dict)
    print(response.json())

def get_request(leet_id):
    response = requests.get(BASE + f"leet-api/leet/{leet_id}")
    print(response.json())

def put_user_request(user_dict):
    response = requests.put(BASE + f"leet-api/user/{user_dict['user_public_id']}", user_dict)
    print(response.json())

def login_put_req(user_dict):
    response = requests.get(BASE + f"leet-api/auth/{user_dict['user_public_id']}")
    print(response.json())


@click.group()
def main():
    """
    Something in the way
    """


@main.command()
@click.option('-u', type=str, required=True, help="Question")
@click.option('-mail', type=str, required=True, help='Time Spent')
@click.option('-password', type=str, required=True, help="Question")
def signup(u, mail, password):
    user_id = random.randint(0, 1000000)  
    user_dict = {
        'username': u,
        'email': mail,
        'password': pbkdf2_sha256.encrypt(password),
        'user_public_id': u + '-' + str(user_id),
        'is_active': False
    }
    
    leetUser.insert_one(user_dict)
    click.echo(f"Signed up successfully as {user_dict['user_public_id']}")


@main.command()
@click.option('-pwd', type=str, required=True, help='Time Password')
@click.option('-user_id', type=str, required=True, help='id')
def auth(pwd, user_id):
    user = leetUser.find_one({'user_public_id': user_id})
    if user and pbkdf2_sha256.verify(pwd, user['password']):
        response = requests.get(f"http://127.0.0.1:5003/api-login/{user['user_public_id']}")
        token = response.json()['token']
        put_token = {"$set":{"token": token}}
        leetUser.update_one({'user_public_id': user_id}, put_token)
    click.echo(f"Your auth token for 24 hours: {user['token']}")


@main.command()
@click.option('-password', type=str, required=True, help='Time Password')
@click.option('-user_id', type=str, required=True, help='id')
@click.option('-token', type=str, required=True, help='Auth token')
def login(password, user_id, token):
    user_dict = {
        'password': password,
        'user_public_id': user_id,
    }

    user = leetUser.find_one({
            'user_public_id': user_dict['user_public_id']
    })
    
    if user and pbkdf2_sha256.verify(user_dict['password'], user['password']):
        make_active = {"$set": {"is_active": True}}
        make_cli = {"$set": {"cli_user": True}}
        leetUser.update_one({"username": user["username"]}, make_active)
        leetUser.update_one({"username": user["username"]}, make_cli)
        click.echo(f"Logged in successfully as {user_dict['user_public_id']}")
    else:
        click.echo("Wrong password or user_id")
    


@main.command()
@click.option('-q', type=str, required=True, help="Question")
@click.option('-t', type=str, required=True, help='Time Spent')
@click.option('-f', type=str, required=True, help='Did you failed or not')
@click.option('-qt', type=str, required=True, help='Question Tag')
@click.option('-u', type=str, required=True, help='Owner id')
def add(q, t, f, qt, u):
    """
    Initialize question, time spent, failed or not and question tag
    """
    commit_dict = {
        'owner_id': u,
        'question': q,
        'time_spent': t,
        'isFailed': f,
        'q_tag': qt,
        'date': datetime.utcnow()
    }
    pickle_out = open("leet.pickle", "wb")
    pickle.dump(commit_dict, pickle_out)


@main.command()
@click.option('-m', type=str, required=True, help='Question Tag')
def commit(m):
    """
    Enter a commit message
    """
    pickle_in = open("leet.pickle", "rb")
    
    commit_dict = pickle.load(pickle_in)
    
    unique_id = random.randint(0, 1000000)

    commit_dict["commit_msg"] = m
    commit_dict["leet_id"] = unique_id
   

    pickle_out = open("leet.pickle", "wb")
    
    pickle.dump(commit_dict, pickle_out)

    pickle_out.close
   

    click.echo(f"Leet created with the id: {unique_id}")


@main.command()
def push():
    pickle_in = open("leet.pickle", "rb")
    commit_dict = pickle.load(pickle_in)

    leetData.insert_one(commit_dict)
    
    