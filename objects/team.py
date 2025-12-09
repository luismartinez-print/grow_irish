import pandas as pd
import seaborn as sns
import streamlit as st
from objects.player import Player

class Team:
    def __init__(self, name, conference):
        self.name = name
        self.conference = conference
        self.roster = []
        self.mean_height = 0
        self.positions = []
        self.years = []


    def create_roster(self, file_path):
        df = pd.read_csv(file_path)

        for row_tuple in df.itertuples(index=False):
            player = Player(
                name = row_tuple.Name,
                height= row_tuple.height,
                year= row_tuple.Class,
                position=row_tuple.POSITION
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
        





        