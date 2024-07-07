import pandas as pd
import numpy as np

matches = pd.read_csv('ipl-matches.csv')

def teamsAPI():
    teams = matches.Team1.unique()
    team_dict = {
        "teams" : teams
    }
    return team_dict

def team_vs_team(team1, team2):
    teams = matches.Team1.unique()

    if (team1 in teams) and (team2 in teams):
        temp_df = matches[((matches['Team1'] == team1) & (matches['Team2'] == team2)) | (
                    (matches['Team1'] == team2) & (matches['Team2'] == team1))]
        total_matches = temp_df.shape[0]
        matches_won_team1 = temp_df["WinningTeam"].value_counts()[team1]
        matches_won_team2 = temp_df["WinningTeam"].value_counts()[team2]
        draws = total_matches - (matches_won_team1 + matches_won_team2)

        result = {
            'total_matches': str(total_matches),
            team1: str(matches_won_team1),
            team2: str(matches_won_team2),
            'draws': str(draws)
        }
        return result

    else:
        message = {"message" : "Invalid Team Name"}
        return message