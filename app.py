import streamlit as st
import pandas as pd
from objects.team import Team


team = Team("Notre Dame Hockey", "ACC")


st.set_page_config(page_title="Grow Irish Project")

st.title("Team Travel Analyzer")

team_name = st.text_input("Enter the name team")

team_conference = st.text_input("Enter the team's conference")

team = Team(team_name, team_conference)

st.divider()

st.subheader("Enter information about the team") #make this look prettier


players = st.file_uploader("Upload the Teams Roster", type='csv')
## add fuction to create player (done)
if players:
    team.create_roster(players)
    st.success("Players successfully uploaded")
    
    st.subheader("Summary Stats")
    team.get_roster_stats()
    st.write(f"The mean height of the {team.name} is {team.mean_height:.2f}")
    if team.mean_weight > 0:
        st.write(f"The mean weight of the team {team.name} is {team.mean_weight:.2f}")
    st.subheader("Position Count Distribution")
    team.get_position_distribution()
    st.subheader("Class Distribution")
    team.get_class_distribution()
    #come up with more ideas for distribution and data analysis

travel = st.file_uploader("Upload Travel Information", type = 'csv')
## add function to create travel info
### Create some summary stats for the traveling information

games = st.file_uploader("Upload Game History", type='csv')
#add function to create games
### Create some summary stats for the games info 



master_button = st.button("Create Analysis")

if master_button:
    st.write("Here is where the whole analysis will be")

    ### Add Some more Stuff here for the whole analysis






