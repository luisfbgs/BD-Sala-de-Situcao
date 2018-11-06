import os
import datetime
import json
from bson.json_util import dumps
from bson.json_util import loads
from flask import Flask, request, jsonify
from pymongo import MongoClient

client = MongoClient('mongodb+srv://adm_sala_st:' + os.environ['DB_PASS'] + os.environ['CLUSTER_U']) 
database = client.sala_db
collection = database.news

db_api = Flask(__name__)

def retrieve_query(place = "", title = "", disease = "", year = 1, month = 1, day = 1, hour = 0):
	return collection.find({"title" : {"$regex" : "^" + title},
							"mod_date" : {"$gte" : datetime.datetime(year, month, day, hour)}})

def insert_query(json_content):
	new_id = collection.insert_one(json_content).inserted_id
	collection.update_one({'_id' : new_id}, {'$set' : {'mod_date' : datetime.datetime.now()}})
	return new_id

def check_input_json(input_json):
	keys = ['source', 'author', 'title', 'description', 'url', 'url_to_image', 'country', 'region', 'score', 'date', 'disease']
	for k in keys:
		assert k in input_json

@db_api.route('/retrieve', methods = ['GET'])
def retrieve():
	place = request.args.get('place', "")
	title = request.args.get('title', "")
	disease = request.args.get('disease', "")
	year = int(request.args.get('year', 1))
	month = int(request.args.get('month', 1))
	day = int(request.args.get('day', 1))
	hour = int(request.args.get('hour', 0))
	
	query_str = retrieve_query(place, title, disease, year, month, day, hour);
	query_str = dumps(query_str)
	return jsonify(json.loads(query_str))
 
@db_api.route('/insert', methods = ['GET'])
def insert():
	content = request.args.get('json', "")
	try:
		json_content = loads(content)
		check_input_json(json_content)
	except:
		return "Fail"
	return str(insert_query(json_content))

if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	db_api.run(host = '0.0.0.0', port = port)
