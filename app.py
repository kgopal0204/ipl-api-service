from flask import Flask, jsonify, request, render_template
import ipl
import balls

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

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

@app.route('/api/team-record')
def team_record():
    team_name = request.args.get('team')
    response = balls.teamAPI(team_name)
    return response

@app.route('/api/batting-record')
def batting_record():
    batsman_name = request.args.get('batsman')
    response = balls.batsmanAPI(batsman_name)
    return response

@app.route('/api/bowling-record')
def bowling_record():
    bowler_name = request.args.get('bowler')
    response = balls.bowlerAPI(bowler_name)
    return response


app.run(debug=True)