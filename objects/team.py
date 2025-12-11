import pandas as pd
import seaborn as sns
import streamlit as st
from objects.player import Player
import os
import googlemaps
from geopy import distance
from objects.game import Game

class Team:
    def __init__(self, name, conference):
        self.name = name
        self.conference = conference
        self.roster = []
        self.mean_height = 0
        self.mean_weight = 0
        self.positions = []
        self.years = []
        self.games = []


    def create_roster(self, file_path):
        df = pd.read_csv(file_path)

        df_columns_upper = [col.upper() for col in df.columns]
        weight_column_exists = "WEIGHT" in df_columns_upper
        

        weight_col_name = None
        if weight_column_exists:
            
            weight_col_name = df.columns[df_columns_upper.index("WEIGHT")]

        for row_tuple in df.itertuples(index=False):
            

            if weight_column_exists:

                player_weight = getattr(row_tuple, weight_col_name)
            else:
 
                player_weight = None

            
            player = Player(
                name = row_tuple.Name,
                height= row_tuple.height,
                year= row_tuple.Class,
                position=row_tuple.POSITION,
                weight=player_weight 
            )
            self.roster.append(player)
    
        for player in self.roster:
            self.positions.append(player.position)
        for player in self.roster:
            self.years.append(player.year)

    def get_roster_stats(self):
        for player in self.roster:
            self.mean_height += player.height
        
        self.mean_height = self.mean_height / len(self.roster)
        
        if self.roster[0].weight is not None:
            for player in self.roster:
                self.mean_weight += player.weight
            self.mean_weight = self.mean_weight / len(self.roster)


    


    def get_position_distribution(self):
        temp_df = pd.DataFrame({
            "Position": self.positions
        })

        count_series = temp_df['Position'].value_counts()

        count_df = count_series.reset_index()

        count_df.columns = ["Position", "Count"]

        st.bar_chart(
            data = count_df.set_index('Position'),
            use_container_width=True
        )
        
    def get_class_distribution(self):
        temp_df = pd.DataFrame({
            "Class": self.years
        })

        count_series = temp_df['Class'].value_counts()

        count_df = count_series.reset_index()

        count_df.columns = ["Class", "Count"]

        st.bar_chart(
            data = count_df.set_index('Class'),
            use_container_width=True
        ) 
    
##### TRavel SEction######
   
    def initialize_client(self):
        API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

        return googlemaps.Client(key='#####') #ADD HASH KEY
    

    def get_travel_info(self, gmaps_client, destination_map:dict):

        ND_HOME = "University of Notre Dame, South Bend, IN"
        ND_AP = "South Bend International Airport, SBN"

        results = []

        nd_coords = gmaps_client.geocode(ND_HOME)[0]['geometry']['location']
        nd_point = distance.Point(nd_coords['lat'], nd_coords['lng'])

        cities = list(destination_map.values())

        for opponent, destination_city in destination_map.items():
            ### This is the driving data
            try:
                matrix = gmaps_client.distance_matrix(
                    origins = [ND_HOME],
                    destinations = [destination_city],
                    mode = 'driving'
                )
                element = matrix['rows'][0]['elements'][0]
                driving_dist = element['distance']['text']
                driving_time = element['duration']['text']
            except Exception:
                driving_dist, driving_time = "API Error", "API Error"
                element = {'status': 'ERROR'}

            #try the flight travel
            try:
                dest_geo = gmaps_client.geocode(destination_city)
                if not dest_geo:
                    dest_coords = {'lat': 0, 'lng': 0}
                    flight_dist, flight_time = "Geocoding Error", "Geocoding Error"
                    element = {'status': 'ZERO_RESULTS'}
                
                else:
                    dest_coords = dest_geo[0]['geometry']['location']
                    dest_point = distance.Point(dest_coords['lat'], dest_coords['lng'])
            
                    flight_miles = distance.distance(nd_point, dest_point).miles
                    flight_dist = f"{flight_miles:,.0f} miles"
                    flight_time = f"{flight_miles / 550:.1f} hours" # 550 mph estimate
            
            except Exception:
                dest_coords = {'lat': 0, 'lng': 0}
                flight_dist, flight_time = "Geocoding Error", "Geocoding Error"
            
            results.append({
                'Opponent': opponent,
                'Destination': destination_city,
                'Driving Distance': driving_dist,
                'Driving Time': driving_time,
                'Flight Distance (mi)': flight_dist,
                'Flight Time (est.)': flight_time,
                'Lat': dest_coords['lat'],
                'Lng': dest_coords['lng'],
                'Status': element['status']
            })

        results_df = pd.DataFrame(results)

        return results_df, nd_coords
        

###### GAMES SECTION #########

    def create_games(self,file_path):
        df = pd.read_csv(file_path)

        for row_tuple in df.itertuples(index=False):
            game = Game(
                game_id = row_tuple.Game_id,
                date = row_tuple.Date,
                season_type= row_tuple.Season_Type,
                home = row_tuple.home,
                opponent= row_tuple.Opponent,
                srs = row_tuple.SRS,
                team_score= row_tuple.Team_Score,
                opponent_score=row_tuple.Opponent_Score,
                result= row_tuple.Result_1
            )
            self.games.append(game)

    def get_srs_comparison(self):

        home = []
        srs = []

        for game in self.games:
            srs.append(game.srs)
            if game.home == 1:
                home.append('Home')
            else:
                home.append('Away')
        


        temp_df = pd.DataFrame({"Location": home, "SRS": srs})

        agg = temp_df.groupby('Location')['SRS'].mean().reset_index()

        st.bar_chart(agg, x = "Location", y = 'SRS')
    
    def get_points_comparison(self):
        home = []
        points = []

        for game in self.games:
            points.append(game.team_score)
            if game.home == 1:
                home.append('Home')
            else:
                home.append('Away')
        


        temp_df = pd.DataFrame({"Location": home, "SRS": points})

        agg = temp_df.groupby('Location')['SRS'].mean().reset_index()

        st.bar_chart(agg, x = "Location", y = 'SRS')

        
    



        