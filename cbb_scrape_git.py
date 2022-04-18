# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 17:17:17 2021

@author: mattb
"""

from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd
from pandas import DataFrame


## List of conferences via sports-reference.com ##

# conf_list = ['aac', 'acc', 'america-east', 'atlantic-10', 'atlantic-sun', 'big-12',
#              'big-east', 'big-sky', 'big-south', 'big-ten','big-west', 'colonial',
#              'cusa', 'horizon', 'ivy', 'maac', 'mac', 'meac', 'mvc', 'mwc', 'northeast',
#              'ovc', 'pac-12', 'patriot', 'sec', 'southern', 'southland', 'summit', 'sun-belt',
#              'swac', 'wac', 'wcc']



## Input conference of interest from list above ##
conf = 'patriot'


## Use Beautiful Soup to scrape table of conference play scores from sports-reference.com ##

sched_response = requests.get(f'https://www.sports-reference.com/cbb/conferences/{conf}/2022-schedule.html')
sched_soup = Soup(sched_response.text, 'lxml')
tables = sched_soup.find_all('table')
schedule = tables[0]
rows = schedule.find_all('tr')


def parse_row(row):
    return [str(x.string) for x in row.find_all('td')]

list_of_parsed_rows = [parse_row(row) for row in rows]

szn_data = DataFrame(list_of_parsed_rows) # Store data in a dataframe using Pandas


## Style dataframe of conference schedule and scores ##

szn_data.columns = 'Away','PTS.A','Home','PTS.H','OT','Notes' # Change column names
szn_data = szn_data.drop(['OT'], axis=1) # Drop OT column
szn_data = szn_data.apply(lambda x: pd.Series(x.dropna().values)) # Drop table break rows
szn_data[['PTS.A','PTS.H']] = szn_data[['PTS.A','PTS.H']].replace({'None':0}) # Change str "None" to "0"
szn_data[['PTS.A','PTS.H']] = szn_data[['PTS.A','PTS.H']].apply(pd.to_numeric) # Change the type of all PTS to int

szn_data.drop(szn_data[szn_data['PTS.A'] == 0].index, inplace = True) # Drop games that were canceled (that had 0 pts)
szn_data = szn_data.reset_index(drop=True)

## Create dataframe for conference standings ##

stand_array = szn_data.Away.unique() # Create an array of all teams in the conference
stand_df = pd.DataFrame(stand_array) # Convert to a dataframe
stand_df[['Win','Loss','Win %']] = 0 # Create columns
stand_df.rename(columns = {0:'Team'}, inplace=True) # Rename Team column
stand_df.set_index('Team', inplace=True)


## Set variables for home court advantage calculation
home_wins = 0
away_wins = 0
HCA = 0
GP = 0

## Create nested Loop ##
## Loop iterates through each row of szn_data dataframe ##
## documenting Wins and Losses for each team in the stand_df dataframe ##

i = 0 # Create a counter
    
while i < len(szn_data): # loop stops once counter reaches the length of the dataframe
    

    home_tag = szn_data.iloc[i]['Home']
    away_tag = szn_data.iloc[i]['Away']    
    home_score = szn_data.iloc[i]['PTS.H']
    away_score = szn_data.iloc[i]['PTS.A']
    
    
    if home_score > away_score:
        home_wins += 1
        stand_df.loc[home_tag][0] += 1
        stand_df.loc[away_tag][1] += 1

    elif away_score > home_score:
        away_wins += 1
        stand_df.loc[away_tag][0] += 1
        stand_df.loc[home_tag][1] += 1

    GP += 1   
    i += 1 
    

## Style and add Win% column to stand_df dataframe ##

stand_df['Win %'] = (stand_df['Win']/(stand_df['Win'] + stand_df['Loss'])).round(3) # Calculate win %
stand_df.sort_values(by=['Win %'], ascending=False, inplace=True) # Sort dataframe by win %
stand_df.reset_index(inplace=True)
size = len(stand_df)
stand_df.insert(0,'Rk',(range(1,size+1))) # Add a rank column
stand_df.set_index('Rk', inplace=True)

print(stand_df.round(3))
