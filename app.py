from flask import Flask, render_template, request, jsonify 
from collections import OrderedDict
import json

app = Flask(__name__)

#method using online service to pull zip code estimation from IP address
def get_zipcode(ip_address):
	try:
		#if running locally, just labels as local host
		if ip_address == "127.0.0.1":
			return("local host")
		#pulls JSON data from API to estimate user zip code per submission
		else:
			response = requests.get("http://ip-api.com/json/{}".format(ip_address))
			js = response.json()
			zip = js["zip"]
			return zip
	except Exception as e:
		return "Unknown"

#reads "database" of zip codes to identify up to the top 3 most freq occuring locations
#for task purposes, "database" is simulated through a text file
def gettopzips(file):
	zips = {}
	f = open(file, "r")
	all_zips = f.readlines()
	for zip in all_zips:
		try:
			zips[zip.strip()] += 1
		except:
			zips[zip.strip()] = 1
	sorted_zips = OrderedDict(sorted(zips.items(), key=lambda t: t[1], reverse=True))
	sorted_keys = list(sorted_zips.keys())
	if len(sorted_keys) == 0:
		return "NONE"
	elif len(sorted_keys) < 3:
		if len(sorted_keys) == 1:
			return sorted_keys[0]
		else:
			return sorted_keys[0] + "<br>" + sorted_keys[1] + "<br>"	
	else:
		return str(sorted_keys)
		#return sorted_keys[0] + "<br>" + sorted_keys[1] + "<br>" + sorted_keys[2]

#Home page for the survey
@app.route("/response")
def index():
	return render_template("index.html")

#Post method for response
#Alerts users of their submission and adds response JSON to "database" and zip code to "database"
#"Database" simulated through text file for task purposes
@app.route("/response", methods=['POST'])
def response():
	input = request.form.get('response')
	id = 'COVID-19'
	data = {'response': input, 'survey_id': id}
	f = open("mockdb.txt", "a")
	json.dump(data, f, indent=2)
	ip_add = request.remote_addr
	zip = get_zipcode(ip_add)
	f.write("\nzip code: " + zip + "\n")
	f.close()
	f2 = open("zips.txt", "a")
	f2.write(zip + "\n")
	f2.close()
	return "Thank you for the following response.<br><br>{<br>response: " + input + "<br>survey_id: " + id + "<br>}"

#Get method for survey data
#returns JSON of each response followed by estimated zip code
#Outputs up to the top 3 most freq zip codes 
@app.route("/survey/<survey_id>", methods=['GET'])
def results(survey_id):
	output_final = ""
	if survey_id == "COVID-19":
		f = open('mockdb.txt', 'r')
		output = f.readlines()
		f.close()
		for line in output:
			output_final += line + "<br>"
		common_zips = gettopzips('zips.txt')
		output_final += "<br><br>Most common zip code(s):<br>" + common_zips
	return output_final

if __name__ == "__main__":
	app.run()
