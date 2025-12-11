import streamlit as st
import pandas as pd
from objects.team import Team
import folium
from streamlit_folium import folium_static
from arenas import cities


#### Main Page Configuration #####
icon = "Nd_athletics_gold_logo_2015.svg.png"
st.set_page_config(page_title="Grow Irish Project", page_icon= icon, layout="wide")

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
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Summary Stats")
        team.get_roster_stats()
        st.write(f"The mean height of the {team.name} is {team.mean_height:.2f}")
        if team.mean_weight > 0:
            st.write(f"The mean weight of the team {team.name} is {team.mean_weight:.2f}")
    with col2:
        st.subheader("Position Count Distribution")
        team.get_position_distribution()
    
    with col3:
        st.subheader("Class Distribution")
        team.get_class_distribution()
    #come up with more ideas for distribution and data analysis

travel = st.file_uploader("Upload Travel Information", type = 'csv')
## add function to create travel info
### Create some summary stats for the traveling information
st.subheader("Distance and destinations map")

gmaps_client = team.initialize_client()


if gmaps_client is None:
    st.warning("Error initializing the client API")

target_cities = cities
df_full, nd_coords = team.get_travel_info(gmaps_client, target_cities)

st.sidebar.header("Filter Destinations")

selected_oponents = st.sidebar.multiselect(
    "Select Away Games",
    options=df_full['Opponent'].unique(),
    default=df_full['Opponent'].to_list()
)

df_filtered = df_full[df_full['Opponent'].isin(selected_oponents)]

st.subheader("Travel Matrix for Selected Games")

st.dataframe(df_filtered.drop(['Lat', 'Lng', 'Status'], axis = 1), use_container_width=True)

st.header("Away Game Map")

m = folium.Map(
    location = [nd_coords['lat'], nd_coords['lng']],
    zoom_start = 4,
    tiles = "CartoDB positron"
)
folium.Marker(
    location = [nd_coords['lat'], nd_coords['lng']],
    popup="Notre Dame",
    icon = folium.Icon(color='green', icon = 'Home')
).add_to(m)

for index, row in df_filtered.iterrows():
    # HTML content for the interactive popup
    html = f"""
    <h4>{row['Opponent']} ({row['Destination']})</h4>
    <p><b>Driving:</b> {row['Driving Distance']} ({row['Driving Time']})</p>
    <p><b>Flying (Est):</b> {row['Flight Distance (mi)']} ({row['Flight Time (est.)']})</p>
    """
    iframe = folium.IFrame(html, width=250, height=130)
    popup = folium.Popup(iframe, max_width=260)

    folium.Marker(
        location=[row['Lat'], row['Lng']],
        popup=popup,
        icon=folium.Icon(color='red', icon='plane')
    ).add_to(m)

    # Render the map in Streamlit
folium_static(m, width=900, height=500)




games = st.file_uploader("Upload Game History", type='csv')
#add function to create games
### Create some summary stats for the games info 

if games:
    team.create_games(games)
    st.success("Games Created!")
    team.get_srs_comparison()



master_button = st.button("Create Analysis")

if master_button:
    st.write("Here is where the whole analysis will be")

    ### Add Some more Stuff here for the whole analysis






