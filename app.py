import streamlit as st
import pandas as pd
from objects.team import Team
import folium
from streamlit_folium import folium_static
from arenas import cities
import plotly.express as px


#### Main Page Configuration #####
icon = "Nd_athletics_gold_logo_2015.svg.png"
st.set_page_config(page_title="Grow Irish Project", page_icon= icon, layout="wide")

st.title("Team Travel Schedule Optimizer")
team_name = "Women's Notre Dame Basketball Team"
team_conference = "ACC"

st.subheader(team_name)
st.subheader(team_conference)

team = Team(team_name, team_conference)

st.divider()

players = "w_basketball1.csv"
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

st.dataframe(df_filtered.drop(['Lat', 'Lng', 'Status'], axis = 1), use_container_width=True,
             hide_index=True)



df_plot = df_filtered[[
    'Destination', 
    'Driving Time (est. hours)', 
    'Flight Time (est. hours)'
]].copy()

# In app.py (near the top, before the st.button block)

# ... (st.multiselect code here) ...

# --- NEW INPUT WIDGET ---
add_time = st.number_input(
    "Enter the estimated time (in hours) required for airport check-in, security, and baggage claim:",
    min_value=0.0,
    max_value=10.0,
    value=3.0, 
    step=0.5,
    format="%.1f",
    key="airport_penalty_input"
)

df_plot['Driving Time (est. hours)'] = pd.to_numeric(df_plot['Driving Time (est. hours)'], errors='coerce')
df_plot['Flight Time (est. hours)'] = pd.to_numeric(df_plot['Flight Time (est. hours)'], errors='coerce') + add_time

df_plot.rename(columns = {
    'Driving Time (est. hours)': 'Driving',
    'Flight Time (est. hours)': 'Flying (Total Est.)'
}, inplace = True)

df_long = pd.melt(
    df_plot,
    id_vars=['Destination'],
    value_vars=['Driving', 'Flying (Total Est.)'],
    var_name='Mode',
    value_name='Time (hours)'
).dropna(subset=['Time (hours)'])
    
    # 3. Create the grouped bar chart
fig = px.bar(
    df_long,
    x='Destination',
    y='Time (hours)',
    color='Mode',
    barmode='group',
    title='Estimated Total Travel Time: Driving vs. Flying (from ND)',
    labels={'Time (hours)': 'Estimated Travel Time (hours)', 'Destination': 'Destination City'},
    color_discrete_map={'Driving': 'darkgreen', 'Flying (Total Est.)': 'darkblue'}
    )
    
fig.update_layout(
    xaxis_title=None, 
    yaxis_title="Estimated Travel Time (hours)",
    legend_title="Travel Mode"
)

st.plotly_chart(fig)

fig2 = px.violin(
    df_long,
    y='Time (hours)',
    x='Mode',
    color='Mode',
    box=True, # Show the box plot inside the violin
    points="all", # Show all individual data points
    title='Distribution of Travel Times by Mode',
    labels={'Time (hours)': 'Travel Time (hours)'},
    color_discrete_map={'Driving': 'darkgreen', 'Flying (Total Est.)': 'darkblue'}
)
st.plotly_chart(fig2)



st.header("Away Game Map")

m = folium.Map(
    location = [nd_coords['lat'], nd_coords['lng']],
    zoom_start = 4,
    tiles = "OpenStreetMap"
)
folium.Marker(
    location = [nd_coords['lat'], nd_coords['lng']],
    popup="Notre Dame",
    icon = folium.CustomIcon(icon)
).add_to(m)

for index, row in df_filtered.iterrows():
    # HTML content for the interactive popup
    html = f"""
    <h4>{row['Opponent']} ({row['Destination']})</h4>
    <p><b>Driving:</b> {row['Driving Distance (mi)']} (mi) ({row['Driving Time (est. hours)']}) (hrs)</p>
    <p><b>Flying (Est):</b> {row['Flight Distance (mi)']} (mi) ({row['Flight Time (est. hours)']}) (hrs)</p>
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

# For optimization of schedule
if 'opt_df' not in st.session_state:
    st.session_state['opt_df'] = None
if 'total_time' not in st.session_state:
    st.session_state['total_time'] = None
if 'city_cords' not in st.session_state:
    st.session_state['city_cords'] = None


st.title("Notre Dame Travel Optimization")
selected_stadiums = st.multiselect("Select the away teams to include",
                                    options= list(target_cities.keys()),
                                    default = list(target_cities)[:8:2],
                                    placeholder= "Chose one or more options")
away_games_filtered = {}
for opponent in selected_stadiums:
    city_address = target_cities[opponent]
    away_games_filtered[opponent] = city_address

if st.button("Optmize Schedule"):

    try:
        with st.spinner("Calculating optimal route..."):
            opt_df, total_time, city_cords = team.get_optimized_schedule(gmaps_client, away_games_filtered)
    
            st.session_state['opt_df'] = opt_df
            st.session_state['total_time'] = total_time
            st.session_state['city_cords'] = city_cords
 
    except Exception as e:
        st.error(f"An error has occurred during optimization")
        st.session_state['opt_df'] = None

    
    
    if st.session_state['opt_df'] is not None:
        opt_df = st.session_state['opt_df']
        total_time = st.session_state['total_time']
        city_cords = st.session_state['city_cords']


        st.header("Optimal Mixed-Mode Travel Schedule")
        st.dataframe(opt_df, hide_index=True)
        st.subheader(f"Total Optimized Travel Time: {total_time:.1f} minutes")


        st.header("Optimal Map for Traveling")
    

        map_locations = {
            name: [data['lat'], data['lng']]
            for name, data in city_cords.items()
        }

        mode_colors = {
            "Drive": "darkgreen",
            "Fly": "darkblue",
            "Error": "red"
        }

        nd_coords_data = city_cords['Notre Dame']

        f = folium.Map(
            location = [nd_coords_data['lat'], nd_coords_data['lng']],
            zoom_start = 4,
            tiles = "OpenStreetMap"
        )

        for city_name, (lat, lon) in map_locations.items():
            if city_name == "Notre Dame":
                color = "green"
                icon = "home"
            else:
                color = 'red'
                icon = "flag"
                        
            folium.Marker(
                location = [lat, lon],
                popup = city_name,
                icon = folium.Icon(color = color, icon = icon)
            ).add_to(f)

        for index, row in opt_df.iterrows():
            origin_name = row['Origin']
            dest_name = row['Destination']
            mode = row['Mode']

            origin_loc = map_locations.get(origin_name)
            dest_loc = map_locations.get(dest_name)

            if origin_loc and dest_loc:
                points  = [origin_loc, dest_loc]

                line_color = mode_colors.get(mode, 'gray')

                folium.PolyLine(
                    points, 
                    color = line_color,
                    weight = 3,
                    opacity = 0.8,
                    popup = f"{row['Stop']}: {origin_name} to {dest_name} ({mode}, {row['Time (min)']} min)"
                ).add_to(f)

        folium_static(f, width = 900, height = 500)





    games = st.file_uploader("Upload Game History", type='csv')
    #add function to create games
    ### Create some summary stats for the games info 

    if games:
        team.create_games(games)
        st.success("Games Created!")
        team.get_srs_comparison()







