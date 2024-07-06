from flask import Flask,jsonify
import ipl

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello Krishna"

@app.route('/api/teams')
def teams():
    teams = ipl.teamsAPI()
    return jsonify(teams)


app.run(debug=True)