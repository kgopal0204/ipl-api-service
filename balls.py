import pandas as pd
import numpy as np
import json

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

matches = pd.read_csv('ipl-matches.csv')
balls = pd.read_csv('ipl-balls.csv')

ball_withmatch = balls.merge(matches, on='ID', how='inner').copy()

ball_withmatch['BowlingTeam'] = ball_withmatch.apply(
    lambda row: row['Team2'] if row['BattingTeam'] == row['Team1'] else row['Team1'], axis=1
)
batter_data = ball_withmatch[balls.columns.values.tolist() + ['BowlingTeam', 'Player_of_Match']]

def team1vsteam2(team, team2):
    df = matches[((matches['Team1'] == team) & (matches['Team2'] == team2)) | (
                (matches['Team2'] == team) & (matches['Team1'] == team2))].copy()
    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp - won - nr

    return {'matchesplayed': mp,
            'won': won,
            'loss': loss,
            'noResult': nr}


def allRecord(team):
    df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)].copy()
    mp = df.shape[0]
    won = df[df.WinningTeam == team].shape[0]
    nr = df[df.WinningTeam.isnull()].shape[0]
    loss = mp - won - nr
    nt = df[(df.MatchNumber == 'Final') & (df.WinningTeam == team)].shape[0]
    return {'matchesplayed': mp,
            'won': won,
            'loss': loss,
            'noResult': nr,
            'title': nt}


def teamAPI(team, matches=matches):
    TEAMS = matches.Team1.unique()
    if team in TEAMS:
        self_record = allRecord(team)
        against = {team2: team1vsteam2(team, team2) for team2 in TEAMS}
        data = {team: {'overall': self_record,
                       'against': against}}
        return json.dumps(data, cls=NpEncoder)
    else:
        message = {'message' : "Invalid Team Name"}
        return json.dumps(message, cls=NpEncoder)

def batsmanRecord(batsman, df):
    if df.empty:
        return np.nan
    out = df[df.player_out == batsman].shape[0]
    df = df[df['batter'] == batsman]
    inngs = df.ID.nunique()
    runs = df.batsman_run.sum()
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
    if out:
        avg = round(runs / out, 2)
    else:
        avg = np.inf

    nballs = df[~(df.extra_type == 'wides')].shape[0]
    if nballs:
        strike_rate = round((runs / nballs) * 100, 2)
    else:
        strike_rate = 0
    gb = df.groupby('ID').sum()
    fifties = gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)].shape[0]
    hundreds = gb[gb.batsman_run >= 100].shape[0]
    try:
        highest_score = gb.batsman_run.sort_values(ascending=False).head(1).values[0]
        hsindex = gb.batsman_run.sort_values(ascending=False).head(1).index[0]
        if (df[df.ID == hsindex].player_out == batsman).sum() == 0:
            highest_score = str(highest_score)
        else:
            highest_score = str(highest_score) + '*'
    except:
        highest_score = gb.batsman_run.max()

    not_out = inngs - out
    mom = df[df.Player_of_Match == batsman].drop_duplicates('ID', keep='first').shape[0]
    data = {
        'innings': inngs,
        'runs': runs,
        'fours': fours,
        'sixes': sixes,
        'avg': avg,
        'strikeRate': strike_rate,
        'fifties': fifties,
        'hundreds': hundreds,
        'highestScore': highest_score,
        'notOut': not_out,
        'mom': mom
    }

    return data


def batsmanVsTeam(batsman, team, df):
    df = df[df.BowlingTeam == team].copy()
    return batsmanRecord(batsman, df)


def batsmanAPI(batsman, balls=batter_data):
    batters = list(set(list(balls['batter']) + list(balls['non-striker'])))
    if batsman in batters:
        df = balls[balls.innings.isin([1, 2])]  # Excluding Super overs
        self_record = batsmanRecord(batsman, df=df)
        TEAMS = matches.Team1.unique()
        against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}
        data = {
            batsman: {'Overall Batting Record': self_record,
                      'Against All Teams Batting Record': against}
        }
    else:
        data = {'message' : 'Invalid Batsman Name'}

    return json.dumps(data, cls=NpEncoder)


bowler_data = batter_data.copy()

def bowlerRun(x):
    if x[0] in ['penalty', 'legbyes', 'byes']:
        return 0
    else:
        return x[1]
bowler_data['bowler_run'] = bowler_data[['extra_type', 'total_run']].apply(bowlerRun, axis=1)

def bowlerWicket(x):
    if x[0] in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']:
        return x[1]
    else:
        return 0
bowler_data['isBowlerWicket'] = bowler_data[['kind', 'isWicketDelivery']].apply(bowlerWicket, axis=1)


def bowlerRecord(bowler, df):

    df = df[df['bowler'] == bowler]
    inngs = df.ID.unique().shape[0]
    nballs = df[~(df.extra_type.isin(['wides', 'noballs']))].shape[0]
    runs = df['bowler_run'].sum()
    if nballs:
        eco = round((runs / nballs) * 6, 2)
    else:
        eco = 0
    fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
    sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]

    wicket = df.isBowlerWicket.sum()
    if wicket:
        avg = round(runs / wicket, 2)
    else:
        avg = np.inf

    if wicket:
        strike_rate = round(nballs / wicket, 2)
    else:
        strike_rate = np.nan

    gb = df.groupby('ID').sum()
    w3 = gb[(gb.isBowlerWicket >= 3)].shape[0]

    best_wicket = gb.sort_values(['isBowlerWicket', 'bowler_run'], ascending=[False, True])[
        ['isBowlerWicket', 'bowler_run']].head(1).values
    if best_wicket.size > 0:

        best_figure = f'{best_wicket[0][0]}/{best_wicket[0][1]}'
    else:
        best_figure = np.nan
    mom = df[df.Player_of_Match == bowler].drop_duplicates('ID', keep='first').shape[0]
    data = {
        'innings': inngs,
        'wicket': wicket,
        'economy': eco,
        'average': avg,
        'strikeRate': strike_rate,
        'fours_conceded': fours,
        'sixes_conceded': sixes,
        'best_figure': best_figure,
        '3+Wickets': w3,
        'mom': mom
    }

    return data


def bowlerVsTeam(bowler, team, df):
    df = df[df.BattingTeam == team].copy()
    return bowlerRecord(bowler, df)


def bowlerAPI(bowler, balls=bowler_data):
    bowlers = list(set(list(balls['batter']) + list(balls['non-striker']) + list(balls.bowler.unique())))
    if bowler in bowlers:
        df = balls[balls.innings.isin([1, 2])]  # Excluding Super overs
        self_record = bowlerRecord(bowler, df=df)
        TEAMS = matches.Team1.unique()
        against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}
        data = {
            bowler: {'Overall Bowling Record': self_record,
                     'Against All Teams Bowling Record': against}
        }
    else:
        data = {"message" : "Invalid Bowler Name"}

    return json.dumps(data, cls=NpEncoder)
