import pandas as pd
import seaborn as sns
import streamlit as st
from objects.player import Player
import os
import googlemaps
from geopy import distance
from geopy.distance import great_circle
from objects.game import Game
import re
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

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

        return googlemaps.Client(key=API_KEY) #ADD HASH KEY
    

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
                driving_dist_text = element['distance']['text']
                distance_value_string = re.sub(r',| km', '', driving_dist_text)
                driving_dist = float(distance_value_string) / 1.6
                driving_time = element['duration']['value'] / 3600
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
                    flight_dist = flight_miles
                    flight_time = flight_miles / 550
            
            except Exception:
                dest_coords = {'lat': 0, 'lng': 0}
                flight_dist, flight_time = "Geocoding Error", "Geocoding Error"
            
            results.append({
                'Opponent': opponent,
                'Destination': destination_city,
                'Driving Distance (mi)': driving_dist,
                'Driving Time (est. hours)': driving_time,
                'Flight Distance (mi)': flight_dist,
                'Flight Time (est. hours)': flight_time,
                'Lat': dest_coords['lat'],
                'Lng': dest_coords['lng'],
                'Status': element['status']
            })

        results_df = pd.DataFrame(results)

        return results_df, nd_coords
    

    def get_driving_time(self, gmaps_client, origin, destination):

        try:
            directions = gmaps_client.directions(origin, destination)
            
            duration_sec = directions[0]['legs'][0]['duration']['value']

            return duration_sec / 60
        except Exception as e:
            print(f"Error with the get driving time")
            return float('inf')
        
    def get_optimized_schedule(self, gmaps_client, away_games: dict):
        #### --- parameters to tweak --- ####
        all_cities = {"Notre Dame": "University of Notre Dame, South Bend, IN"}
        avg_flight_speed = 500 #mi/hr
        airport_penalty = 150
        miles_to_minutes_conversion =  60 / avg_flight_speed
        all_cities.update(away_games)

        city_coords = {}

        for name, address in all_cities.items():
            try:
                geo_result = gmaps_client.geocode(address)
                if not geo_result:
                    print("Error Geocoding mistake")
                    return None

                loc = geo_result[0]['geometry']['location']
                city_coords[name] = {'lat': loc['lat'], 'lng': loc['lng'], 'address': address}
            
            except Exception as e:
                print(f"Error {name} not found {e}")
                return None, f'Error in geocoding'
            
        city_names = list(city_coords.keys())

        city_data = [(name, data['lat'], data['lng']) for name, data in city_coords.items()]

        time_matrix, city_names = self.get_combined_matrix(gmaps_client, city_data)

        solution, routing, manager = self.solve_mixed_mode_route(time_matrix, city_names, start_node_index=0)

        if not solution:
            return None, "Solver failed, try again"
        
        route_indicies = []
        index = routing.Start(0)

        while not routing.IsEnd(index):
            route_indicies.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        
        route_indicies.append(manager.IndexToNode(index))

        optimal_route = [] # storing the results
        total_time_min = 0

        for i in range(len(route_indicies) - 1):
            origin_idx = route_indicies[i]
            dest_indx = route_indicies[i+1]

            origin_name = city_names[origin_idx]
            dest_name = city_names[dest_indx]

            cost = time_matrix[origin_idx][dest_indx]

            t_drive = self.get_driving_time(gmaps_client, city_coords[origin_name]['address'], city_coords[dest_name]['address'])

            dist_miles = great_circle(
                (city_data[origin_idx][1], city_data[origin_idx][2]),
                (city_data[dest_indx][1], city_data[dest_indx][2])
            ).miles

            t_flight_minutes = dist_miles * miles_to_minutes_conversion
            t_fly = t_flight_minutes + airport_penalty


            if abs(cost - int(t_drive)) < 1:
                mode = "Drive"
            elif abs(cost - int(t_fly)) < 1:
                mode = "Fly"
            else:
                mode = "Error (Mode Mismatch)"
            
            total_time_min += cost

            optimal_route.append({
                'Stop': i + 1,
                'Origin': origin_name,
                'Destination': dest_name,
                'Mode': mode,
                'Time (min)': cost
            })

        df_route = pd.DataFrame(optimal_route)
        return df_route, total_time_min, city_coords



    def get_combined_matrix(self, gmaps_client, city_data):
        avg_flight_speed = 500 #mi/hr
        airport_penalty = 150
        miles_to_minutes_conversion =  60 / avg_flight_speed

        num_cities = len(city_data)
        time_matrix = [[0] * num_cities for _ in range(num_cities)]
        city_names = [name[0] for name in city_data]

        for i in range(num_cities):
            for j in range(num_cities):
                if i == j:
                    continue
                origin_name, origin_lat, origin_lng = city_data[i]
                dest_name, dest_lat, dest_lng = city_data[j]

                ####---- driving Time ----####
                t_drive = self.get_driving_time(gmaps_client, origin_name, dest_name)

                ###----- Flying Time ----####
                distance_miles = great_circle((origin_lat, origin_lng), (dest_lat, dest_lng)).miles
                t_flight_minutes = distance_miles * miles_to_minutes_conversion

                t_fly = t_flight_minutes + airport_penalty

                combined_time = int(min(t_drive, t_fly))

                time_matrix[i][j] = combined_time
        
        return time_matrix, city_names
    
    def solve_mixed_mode_route(self, time_matrix, city_names, start_node_index = 0):
        num_nodes = len(time_matrix)
        manager = pywrapcp.RoutingIndexManager(num_nodes, 1, start_node_index)
        routing = pywrapcp.RoutingModel(manager)

        def transit_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return time_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(transit_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    
        solution = routing.SolveWithParameters(search_parameters)


        if solution:
            return solution, routing, manager
        
        return None, None, None
    


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


        
    



        