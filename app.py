from flask import Flask, jsonify, request
import ipl

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello Krishna"

@app.route('/api/teams')
def teams():
    teams = ipl.teamsAPI()
    return jsonify(teams)

@app.route('/api/teamvsteam')
def teamvsteam():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    response = ipl.team_vs_team(team1, team2)

    return jsonify(response)

app.run(debug=True)